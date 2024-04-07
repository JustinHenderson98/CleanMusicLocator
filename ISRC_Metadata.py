from dataclasses import dataclass

@dataclass
class ISRCMetadata:
    duration: str
    recordingVersion: str
    isValidIsrc: str
    recordingYear: str
    recordingArtistName: str
    isExplicit: str
    isrc: str
    isrcFailureCode: str
    recordingTitle: str
    id: str

