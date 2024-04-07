# Clean Music Locator

The Clean Music Locator was created to be able to identify tracks in your music library that contain clean or censored versions of a song.

## Description

The application works by doing the following for each song in your music library:

1. Parse the song for ISRC metadata using ffprobe
  a. If ISRC metadata is not found the song is skipped and an error is logged.
2. If the ISRC already exists in the database the following steps are skipped
3. Lookup the track in https://isrc.soundexchange.com/
  a. The metadata returned *should* contain whether the track is explicit. But this is not garunteed.
  b. If the metadata cannot be found in https://isrc.soundexchange.com/ the track is marked as being non-explicit.
4. If the track is explicit add it to the database. We don't need to look if an explicit version exists.
5. Use metadata from https://isrc.soundexchange.com/ to search for the song by name on https://isrc.soundexchange.com/. This will return a list of tracks matching the artist, song title, and year. This may fail and the track will be marked as not having an explicit version. 
6. Validate that an explicit version of the song exists in the list of matches.
7. Save the song with it's metadata to the database.  

## Getting Started

### Dependencies

#### Python
* Python interpreter 3.9
* Requests package
  * ```pip install requests```

#### Operating System
* Linux
  * ffmpeg/ffprobe is installed
    * ```apt-get install ffmpeg`` 
* Windows
  * ffprobe is installed.
    * Install ffmpeg with Choclatey
      * https://community.chocolatey.org/packages/ffmpeg
    * Alternatively ffprobe can be manually installed, but must be added to the PATH.
  * Windows is not officially supported due to a bug with the ffprobe3-python and utf-32 chars in song metadata. Your milage may vary.   

#### sqlite3
  * A way to view and interact with the sqlite database.
  * One of:
    * SQLITE3 database command line tool
      * ```apt-get install sqlite3```
    * [https://sqlitebrowser.org/dl/](https://sqlitebrowser.org/dl/)
    * Your favorite SQLite3 quering environment

### Executing program

Arguments:
* directory(required): Directory of your music library. 
* -s, --sleep (optional): Number of milliseconds to sleep between processing songs. This rate limits connections to the soundexchange api 

Process your music library at /mnt/d/Music/ with 500 milliseconds between calls to soundexchange.
```
python3 main.py /mnt/d/Music/ -s 500
```

### Post Execution

After the Clean Music Locator program is ran we need examine the results.

Open music.db with your favorite SQLITE3 environment.

Execute the following commnad to identify where you have clean versions of your music
```SELECT * FROM music WHERE isExplicit="False" AND doesExplicitExist="True"```

It is also a good idea to check the log ```myapp.log``` to see what tracks contained errors for manual review. 

## Authors
Justin Henderson


## Version History
* 0.1
    * Initial Release

## License

This project is licensed under the GPLv3 License - see the LICENSE.txt file for details

## Acknowledgments

Inspiration, code snippets, etc.
* [ffprobe3-python3](https://github.com/jboy/ffprobe3-python3)
* [https://isrc.soundexchange.com/](https://isrc.soundexchange.com/)
