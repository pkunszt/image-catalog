from typing import Pattern
from data.video import Video, InvalidVideoError
from data.image import Image, InvalidImageError
from data.other import Other, InvalidOtherError
from tools import Constants
import os
import io
import hashlib
import exifread
import pyheif
import subprocess
import inspect
import re
from datetime import datetime


class FactoryError(ValueError):
    def __init__(self, message: str):
        super().__init__(message)


class FactoryZeroFileSizeError(ValueError):
    def __init__(self, message: str):
        super().__init__(message)


class Factory:
    _duration: Pattern[str] = re.compile('.*(?P<hour>\d\d):(?P<min>\d\d):(?P<sec>\d\d)\.(?P<msec>\d+).*')

    def __init__(self):
        pass

    @staticmethod
    def from_elastic_entry(e):
        if e.kind == Constants.IMAGE_KIND:
            item = Image()
        elif e.kind == Constants.VIDEO_KIND:
            item = Video()
        elif e.kind == Constants.OTHER_KIND:
            item = Other()
        else:
            raise FactoryError(f"Entry mismatch, wrong kind {e.kind} found for: {e.name}; id:{e.meta.id}")

        item.full_path = os.path.join(e.path, e.name)
        if e.type != item.type:
            raise FactoryError(f"Type mismatch for {e.name}")
        if e.kind != item.kind:
            raise FactoryError(f"Kind mismatch for {e.name}")
        for attr, value in inspect.getmembers(e, lambda a: not(inspect.isroutine(a))):
            if attr not in Constants.leave_out_when_reading_from_elastic:
                setattr(item, attr, value)
        if item.hash != e.hash:
            raise FactoryError(f"Hash mismatch for {e.name}")
        if item.path_hash != e.path_hash:
            raise FactoryError(f"Path-hash mismatch for {e.name}")
        item.id = e.meta.id

        return item

    @staticmethod
    def from_path(path: str):
        """Create an Image or Video object based on a path name to one.
        Will throw exceptions if the item is neither or if it does not exist"""
        try:
            return Factory.__image_from_directory_item(path)
        except InvalidImageError:
            try:
                return Factory.__video_from_directory_item(path)
            except InvalidVideoError:
                try:
                    return Factory.__other_from_directory_item(path)
                except InvalidOtherError:
                    raise FactoryError(f"Path {path} is neither image nor video nor other")

    @staticmethod
    def from_dropbox(entry):
        """Create an Image or Video object based on the dropbox path given"""
        try:
            result = Image()
            result.full_path = entry['path']
        except InvalidImageError:
            try:
                result = Video()
                result.full_path = entry['path']
            except InvalidVideoError:
                try:
                    result = Other()
                    result.full_path = entry['path']
                except InvalidOtherError:
                    raise FactoryError(f"Path {entry['path']} is neither image nor video nor other")
        del entry['path']
        return result.update(entry)

    @staticmethod
    def __image_from_directory_item(path: str) -> Image:
        image = Image()
        Factory.__entry_from_directory_item(image, path)
        Factory.__add_captured_time_and_location(image, path)
        return image

    @staticmethod
    def __add_captured_time_and_location(image: Image, path: str):
        with open(path, 'rb') as file:
            if image.type == 'heic':
                i = pyheif.read_heif(file)
                for metadata in i.metadata or []:
                    if metadata['type'] == 'Exif':
                        file = io.BytesIO(metadata['data'][6:])  # for some reason there is a leading 'Exif00' .. ignore

            tags = exifread.process_file(file, details=False)
            if tags:
                if Constants.exif_date_time_original in tags.keys():
                    try:
                        dt = datetime.strptime(str(tags[Constants.exif_date_time_original]),
                                               Constants.exif_date_time_format)
                    except ValueError as e:
                        print(e)
                        print(image.full_path)
                    else:
                        image.captured = dt.timestamp() * 1000
                if Constants.GPS['lat'] in tags.keys() and Constants.GPS['lon'] in tags.keys():
                    lat = Factory.__coord_from_dms(tags[Constants.GPS['lat']].values,
                                                   tags[Constants.GPS['latR']].values)
                    lon = Factory.__coord_from_dms(tags[Constants.GPS['lon']].values,
                                                   tags[Constants.GPS['lonR']].values)
                    image.set_location_from_lat_lon(lat, lon)
                if Constants.exif_width in tags.keys():
                    image.dimensions = f"{tags[Constants.exif_width].printable}x{tags[Constants.exif_height].printable}"

    @staticmethod
    def __coord_from_dms(dms, ref):
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
                                 '-v', f"{os.path.abspath(video.path)}:/files", 'sjourdan/ffprobe',
                                f"/files/{video.name}"], capture_output=True)
        try:
            lines = output.stderr.decode("utf-8").splitlines()
        except UnicodeDecodeError:
            lines = Factory.mydecode(output.stderr).splitlines()
        for line in lines:
            if line.find("Duration") > 0:
                d = Factory._duration.match(line)
                if d:
                    video.duration = int(d.group('hour'))*3600 + int(d.group('min'))*60 + int(d.group('sec'))
            if line.find("creation_time") > 0:
                try:
                    video.captured = datetime.strptime(line[line.find(':')+2:],
                                                       Constants.video_duration_format).timestamp() * 1000
                except ValueError:
                    try:
                        video.captured = datetime.strptime(line[line.find(':')+2:].rstrip(),
                                                           Constants.video_duration_format2).timestamp() * 1000
                    except ValueError as e:
                        print(line)
                        print(video)
                        print(lines)
                        raise e

    @staticmethod
    def __other_from_directory_item(path: str) -> Other:
        other = Other()
        Factory.__entry_from_directory_item(other, path)
        return other

    @staticmethod
    def __entry_from_directory_item(e, path: str):
        e.full_path = path
        st = os.stat(path)
        e.modified = st.st_mtime * 1000
        e.size = st.st_size
        if e.size == 0:
            raise FactoryZeroFileSizeError(path)
        e.checksum = Factory.checksum(path)

    @staticmethod
    def checksum(filename: str) -> str:
        """Return the hex representation of the checksum on the full binary using the same method as dropbox.
        See the description at https://www.dropbox.com/developers/reference/content-hash . Needs full path as input."""
        hasher = DropboxHash()
        with open(filename, "rb") as f:
            for chunk in iter(lambda: f.read(DropboxHash.block_size), b""):
                hasher.update(chunk)
        return hasher.dropbox_hash

    @staticmethod
    def diff(base, update) -> dict:
        if type(base) is not type(update):
            raise FactoryError(f"Diff on different types. One:{repr(base)} and Two:{repr(update)}")

        return base.diff(update)

    @staticmethod
    def mydecode(binary) -> str:
        decoded = ""
        for i in binary:
            if i < 128:
                decoded += chr(i)
        return decoded


class DropboxHash:
    block_size = 1024 * 1024 * 4

    def __init__(self):
        self._hasher = hashlib.sha256()

    def update(self, chunk):
        h = hashlib.sha256()
        h.update(chunk)
        self._hasher.update(h.digest())

    @property
    def dropbox_hash(self):
        return self._hasher.hexdigest()
