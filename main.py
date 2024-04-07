import os
import argparse

import ffprobePython.ffprobe3
from Song_Metadata import SongMetadata
from ISRC_Metadata import ISRCMetadata
from ffprobePython import ffprobe3
import requests
import json
import sqlite3
from time import sleep
import logging
logger = logging.getLogger(__name__)

RequestUrl = "https://isrc-api.soundexchange.com/api/ext/recordings"
authToken = "Token 1107ceca92667a15e8fc28acbcc789c90c09f491"

search_payload = {
    "searchFields": {
        "recordingArtistName": {
            "value": ""
        },
        "recordingTitle": {
            "value": ""
        },
        "releaseName": {
            "value": ""
        },
        "releaseYear": "",
        "recordingVersion": {
            "value": ""
        },
        "recordingYear": "",
        "recordingType": ""
    },
    "start": 0,
    "number": 100,
    "showReleases": False
}


def GetAllMusicFiles(root_dir: str) -> list[str]:
    """Gets all files in a directory recursively that are flac, opus, mp3
    :returns list of music files
    """
    files = []
    for r, d, f in os.walk(root_dir):
        for file in f:
            if '.flac' in file or '.opus' in file or '.mp3' in file:
                files.append(os.path.join(r, file))
    return files

def GetTrackMetaData(song_file_path:str) -> SongMetadata:
    try:
        metadata = ffprobe3.probe(song_file_path)
    except Exception:
        logger.error(f"Could not probe file for metadata. path: {song_file_path}")
        return None
    for s in metadata.streams:
        if isinstance(s, ffprobePython.FFaudioStream):
            try:
                tags = s.parsed_json['tags']
            except:
                return None
            try:
                artist = tags['ARTIST']
            except:
                artist = ""
            try:
                album_artist = tags['album_artist']
            except:
                album_artist = ""
            try:
                title = tags['TITLE']
            except:
                title = ""
            #TODO fix year
            try:
                year = tags['DATE']
            except:
                year = ""
            try:
                isrc = tags['ISRC']
            except:
                isrc = "error"
            meta = SongMetadata(Artist=artist, AlbumArtist=album_artist, Title=title, Year=year, ISRC=isrc, FilePath=song_file_path)
            """
            Assuming streams[0] is FFaudioStream
            metadata.streams[0].parsed_json['tags']
            Tags = {
            TITLE: STR,
            ARTIST: STR,
            ALBUM: STR,
            ISRC: STR,
            DATE: STR
            }
            """
            return meta
    logger.error(f"Could not find audio stream on file. path: {song_file_path}")
    return None

def GetISRCMetadata(song:SongMetadata) -> ISRCMetadata:
    """
    Sample payload:
    {"searchFields":{"isrc":"CAUM81700077"},"start":0,"number":10,"showReleases":false}

    :param song:
    :return:
    """
    data = f'{{"searchFields":{{"isrc":"{song.ISRC}"}},"start":0,"number":10,"showReleases":false}}'
    s = requests.session()
    s.headers.update({'Authorization': authToken})
    r = s.post(RequestUrl, data=data)
    print(r.text)
    try:
        json_obj = json.loads(r.text)
    except Exception as e:
            logger.error(f"Could not decode song. ISRC: {song.ISRC}; path: {song.FilePath}; json: {r.text}; exception: {e}")
            return None

    if len(json_obj['recordings']) == 0:
        logger.error(f"Could not lookup information on song. ISRC: {song.ISRC}; path: {song.FilePath}")
        return None

    metadata = ISRCMetadata(**json_obj['recordings'][0])
    return metadata

def DoesExplicitVersionExist(song:ISRCMetadata) -> bool:
    global search_payload
    search_payload["searchFields"]["recordingArtistName"]["value"] = song.recordingArtistName
    search_payload["searchFields"]["recordingTitle"]["value"] = song.recordingTitle
    search_payload["searchFields"]["recordingYear"] = song.recordingYear
    payload = json.dumps(search_payload)
    s = requests.session()
    s.headers.update({'Authorization': authToken})
    r = s.post(RequestUrl, data=payload)
    print(r.text)
    explict = False
    try:
        dump = json.loads(r.text)
    except Exception as e:
        logger.error(f"Could not parse response from api. API response: {r.text}; exception: {e}; Song:{song.isrc}")
        return False

    for rec in dump["recordings"]:
        if rec["isExplicit"] == "True":
            explict = True
    return explict
    

if __name__ == '__main__':
    logging.basicConfig(filename='myapp.log', level=logging.INFO)
    
    parser = argparse.ArgumentParser(
        prog='Clean Music Locator',
        description='Clean Music Locator finds music in your library that are clean when an explict version exists')
    parser.add_argument('directory', type=str, help='Root directory of the music to be scanned')
    parser.add_argument('-s', "--sleep", type=int, default=1000, help='Milliseconds to wait between calls')
    args1 = parser.parse_args()
    song_paths = GetAllMusicFiles(args1.directory)
    db_connection = sqlite3.connect("music.db")
    
    """
    db -> dict[str(ISRC), ]
    """
    db_cursor = db_connection.cursor()
    metadata_list = []
    try:
        for song in song_paths:
            logger.info(f"Starting lookup. path: {song}")
            print(f"Song: {song}")
            data = GetTrackMetaData(song)
            if data is None:
                continue
            rows = db_cursor.execute("SELECT isrc from music where isrc =?", [data.ISRC]).fetchall()
            if len(rows) != 0:
                logger.info(f"Song already in db. Skipping. path: {song}")
                continue
            # get metadata
            isrcMetadata = GetISRCMetadata(data)
            if isrcMetadata is None:
                continue
            if isrcMetadata.isExplicit == "True":
                doesExplicitExist = True
            else:    
                doesExplicitExist = DoesExplicitVersionExist(isrcMetadata)
            db_cursor.execute("INSERT INTO music VALUES (?,?,?,?,?,?,?,?,?,?,?)", 
                                     [data.ISRC,\
                                    isrcMetadata.recordingTitle,\
                                    isrcMetadata.isrcFailureCode,\
                                    isrcMetadata.recordingArtistName,\
                                    isrcMetadata.recordingYear,\
                                    isrcMetadata.isValidIsrc,\
                                    isrcMetadata.recordingVersion,\
                                    isrcMetadata.duration,\
                                    isrcMetadata.isExplicit,\
                                    str(doesExplicitExist),\
                                    data.FilePath
                                         ])
            print(f"Added {data.ISRC} to db")
            logger.info(f"Finished lookup. path: {song}")
            sleep(args1.sleep/1000)
    except Exception as e:
        print(e)
    finally:
        db_cursor.close()
        db_connection.commit()
        db_connection.close()      





