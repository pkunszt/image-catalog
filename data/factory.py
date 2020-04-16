from data.video import Video, InvalidVideoError
from data.image import Image, InvalidImageError
import os
import hashlib
import exifread
import subprocess
import re
from datetime import datetime


class FactoryError(ValueError):
    def __init__(self, message: str):
        super().__init__(message)


class Factory:
    _exif_date_time_original: str = "EXIF DateTimeOriginal"
    _exif_date_time_format: str = "%Y:%m:%d %H:%M:%S"
    _video_duration_format: str = "%Y-%m-%d %H:%M:%S"
    _GPS: dict = dict(latR="GPS GPSLatitudeRef",
                      lat="GPS GPSLatitude",
                      lonR="GPS GPSLongitudeRef",
                      lon="GPS GPSLongitude"
                      )
    _duration = re.compile('.*(?P<hour>\d\d):(?P<min>\d\d):(?P<sec>\d\d)\.(?P<msec>\d+).*')

    def __init__(self):
        pass

    @staticmethod
    def from_elastic_entry(e):
        if e.kind == 0:
            item = Image()
        elif e.kind == 1:
            item = Video()
        else:
            raise FactoryError(f"Entry mismatch, wrong kind {e.kind} found for: {e.name}; id:{e.meta.id}")

        item.name = e.name
        if e.type != item.type:
            raise FactoryError(f"Type mismatch for {e.name}")
        item.path = e.path
        item.size = e.size
        item.checksum = e.checksum
        item.modified = e.modified
        if item.hash != e.hash:
            raise FactoryError(f"Hash mismatch for {e.name}")
        item.id = e.meta.id

        return item

    @staticmethod
    def from_path(path: str):
        """Create an Image or Video object based on a path name to one.
        Will throw exceptions if the item is neither or if it does not exist"""
        try:
            return Factory.__image_from_directory_item(path)
        except InvalidImageError:
            pass

        try:
            return Factory.__video_from_directory_item(path)
        except InvalidVideoError:
            pass

        raise FactoryError(f"Path {path} is neither image nor video")

    @staticmethod
    def __image_from_directory_item(path: str) -> Image:
        image = Image()
        Factory.__entry_from_directory_item(image, path)
        Factory.__add_captured_time_and_location(image, path)
        return image

    @staticmethod
    def __add_captured_time_and_location(image: Image, path: str):
        with open(path, 'rb') as file:
            tags = exifread.process_file(file)
            if Factory._exif_date_time_original in tags.keys():
                dt = datetime.strptime(str(tags[Factory._exif_date_time_original]), Factory._exif_date_time_format)
                image.captured = dt.timestamp()
            if Factory._GPS['lat'] in tags.keys() and Factory._GPS['lon'] in tags.keys():
                lat = Factory.__get_coord_from_gps(tags[Factory._GPS['lat']].values, tags[Factory._GPS['latR']].values)
                lon = Factory.__get_coord_from_gps(tags[Factory._GPS['lon']].values, tags[Factory._GPS['lonR']].values)
                image.location = f"{lat},{lon}"

    @staticmethod
    def __get_coord_from_gps(dms, ref):
        factor = 1
        if ref in ['S', 'W']:
            factor = -1

        coord = dms[0].num / dms[0].den
        coord += dms[1].num / dms[1].den / 60.0
        coord += dms[2].num / dms[2].den / 3600.0

        return factor * round(coord, 5)

    @staticmethod
    def __video_from_directory_item(path: str) -> Video:
        video = Video()
        Factory.__entry_from_directory_item(video, path)
        Factory.__add_video_length_and_captured_time(video)
        return video

    @staticmethod
    def __add_video_length_and_captured_time(video: Video):
        output = subprocess.run(['docker', 'run', '--rm',
                                 '-v', f"{video.path}:/files", 'sjourdan/ffprobe',
                                f"/files/{video.name}"], capture_output=True)
        lines = output.stderr.decode("utf-8").splitlines()
        for line in lines:
            if line.find("Duration") > 0:
                d = Factory._duration.match(line)
                video.duration = int(d.group('hour'))*3600 + int(d.group('min')*60) + int(d.group('sec'))
            if line.find("creation_time") > 0:
                video.captured = datetime.strptime(line[line.find(':')+2:], Factory._video_duration_format).timestamp()

    @staticmethod
    def __entry_from_directory_item(e, path: str):
        e.full_path = path
        st = os.stat(path)
        e.modified = st.st_mtime
        e.size = st.st_size
        e.checksum = Factory.checksum(path)

    @staticmethod
    def checksum(filename: str) -> str:
        """Return the hex representation of the checksum on the full binary using blake2b. Needs full path."""
        file_hash = hashlib.blake2b()
        with open(filename, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                file_hash.update(chunk)
        return file_hash.hexdigest()

    @staticmethod
    def diff(base, update) -> dict:
        if type(base) is not type(update):
            raise FactoryError(f"Diff on different types. One:{repr(base)} and Two:{repr(update)}")

        return base.diff(update)
