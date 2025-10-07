from pymediainfo import MediaInfo

def get_mediainfo_data(filepath: str) -> dict:
    """Parse media file using pymediainfo."""
    return MediaInfo.parse(filepath).to_data()
