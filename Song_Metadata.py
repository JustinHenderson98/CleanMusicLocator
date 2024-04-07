from dataclasses import dataclass

@dataclass
class SongMetadata:
    Artist: str
    Title: str
    Year: str
    ISRC: str
    AlbumArtist: str
    FilePath: str
