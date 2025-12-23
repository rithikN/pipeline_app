import magic
import ffmpeg
from pymediainfo import MediaInfo
from PIL import Image
import OpenEXR
import Imath
import json
import struct

class DCCFileMetadataExtractor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.mime_type = self.detect_file_type()
        self.file_type = self.identify_file_category()

    def detect_file_type(self):
        """Detect the MIME type of the file using python-magic."""
        mime = magic.Magic(mime=True)
        return mime.from_file(self.file_path)

    def identify_file_category(self):
        """Identifies if the file belongs to a DCC or media type."""
        dcc_file_types = {
            "Maya ASCII": (".ma", "text/plain"),
            "Maya Binary": (".mb", "application/octet-stream"),
            "Blender": (".blend", "application/octet-stream"),
            "Photoshop": (".psd", "image/vnd.adobe.photoshop"),
            "TVPaint": (".tvpp", "application/octet-stream"),
            "Moho": (".moho", "application/json"),
        }
        media_file_types = {
            "EXR": "image/x-exr",
            "MOV": "video/quicktime",
            "MP4": "video/mp4",
            "JPG": "image/jpeg",
            "PNG": "image/png",
            "TIFF": "image/tiff"
        }
        for file_type, (extension, expected_mime) in dcc_file_types.items():
            if self.file_path.endswith(extension) or self.mime_type == expected_mime:
                return file_type
        for file_type, expected_mime in media_file_types.items():
            if self.mime_type == expected_mime:
                return file_type
        return "Unknown"

    def extract_metadata(self):
        """Extract metadata based on file type."""
        if self.file_type in ["Maya ASCII", "Maya Binary"]:
            return self.extract_maya_metadata()
        elif self.file_type == "Blender":
            return self.extract_blender_metadata()
        elif self.file_type == "Photoshop":
            return self.extract_photoshop_metadata()
        elif self.file_type == "TVPaint":
            return self.extract_tvpaint_metadata()
        elif self.file_type == "Moho":
            return self.extract_moho_metadata()
        elif self.file_type in ["EXR", "MOV", "MP4", "JPG", "PNG", "TIFF"]:
            return self.extract_media_metadata()
        else:
            return {"Error": "Unsupported file format"}

    def extract_maya_metadata(self):
        """Extract metadata from Maya (.ma/.mb) files."""
        if self.file_type == "Maya ASCII":
            with open(self.file_path, "r", encoding="utf-8") as file:
                lines = file.readlines()
            metadata = {"File Type": "Maya ASCII (.ma)", "Maya Version": None}
            for line in lines[:50]:
                if line.startswith("fileInfo"):
                    import re
                    match = re.search(r'"mayaVersion" "(.*?)"', line)
                    if match:
                        metadata["Maya Version"] = match.group(1)
                    break
            return metadata
        elif self.file_type == "Maya Binary":
            with open(self.file_path, "rb") as file:
                header = file.read(24)
            version = struct.unpack(">I", header[20:24])[0]
            return {"File Type": "Maya Binary (.mb)", "Maya Version": version}

    def extract_blender_metadata(self):
        """Extract metadata from Blender (.blend) files."""
        try:
            with open(self.file_path, "rb") as f:
                header = f.read(12)
                if not header.startswith(b'BLENDER'):
                    return {"Error": "Invalid .blend file"}
                blender_version = header[-3:].decode("utf-8")
                pointer_size = 8 if header[7:8] == b'-' else 4
                endianness = "Big Endian" if header[8:9] == b'V' else "Little Endian"
                return {"File Type": "Blender", "Blender Version": blender_version, "Pointer Size": pointer_size,
                        "Endianness": endianness}
        except Exception as e:
            return {"Error": str(e)}

    def extract_photoshop_metadata(self):
        """Extract metadata from Photoshop (.psd) files."""
        from psd_tools import PSDImage
        psd = PSDImage.open(self.file_path)
        return {"File Type": "Photoshop", "Width": psd.width, "Height": psd.height, "Number of Layers": len(psd)}

    def extract_tvpaint_metadata(self):
        """Extract metadata from TVPaint (.tvpp) files."""
        try:
            with open(self.file_path, "rb") as file:
                header = file.read(16)
                if not header.startswith(b'TVPP'):
                    return {"Error": "Invalid TVPaint file"}
                version = struct.unpack(">I", header[4:8])[0]
                frame_count = struct.unpack(">I", header[8:12])[0]
                return {"File Type": "TVPaint (.tvpp)", "TVPaint Version": version, "Frame Count": frame_count}
        except Exception as e:
            return {"Error": str(e)}

    def extract_moho_metadata(self):
        """Extract metadata from Moho (.moho) files."""
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
            return {"File Type": "Moho", "Moho Version": data.get("moho_version", "Unknown"),
                    "Frame Rate": data.get("fps", "Unknown")}
        except Exception as e:
            return {"Error": str(e)}

    def extract_media_metadata(self):
        """Extract metadata from EXR, MOV, MP4, PNG, JPG, TIFF."""
        if self.file_type in ["MOV", "MP4"]:
            return self.extract_video_metadata()
        elif self.file_type in ["JPG", "PNG", "TIFF"]:
            return self.extract_image_metadata()
        elif self.file_type == "EXR":
            return self.extract_exr_metadata()
        else:
            return {"Error": "Unsupported media file"}

    def extract_video_metadata(self):
        """Extract metadata from video files (MP4, MOV)."""
        media_info = MediaInfo.parse(self.file_path)
        for track in media_info.tracks:
            if track.track_type == "Video":
                return {"File Type": "Video", "Resolution": f"{track.width}x{track.height}", "FPS": track.frame_rate,
                        "Codec": track.codec_id}

    def extract_image_metadata(self):
        """Extract metadata from image files (PNG, JPG, TIFF)."""
        with Image.open(self.file_path) as img:
            return {"File Type": "Image", "Resolution": img.size, "Format": img.format}

    def extract_exr_metadata(self):
        """Extract metadata from OpenEXR (.exr) files."""
        exr_file = OpenEXR.InputFile(self.file_path)
        header = exr_file.header()
        resolution = (header['dataWindow'].max.x - header['dataWindow'].min.x + 1, header['dataWindow'].max.y - header['dataWindow'].min.y + 1)
        return {"File Type": "EXR", "Resolution": f"{resolution[0]}x{resolution[1]}", "Compression": header.get('compression', 'Unknown')}

# Example Usage
if __name__ == "__main__":
    print("DCC Meta Extractor")
    pass
# file_path = "example.blend"
# extractor = DCCFileMetadataExtractor(file_path)
# print(extractor.extract_metadata())
