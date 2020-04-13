from data.video import Video, InvalidVideoError
from data.image import Image, InvalidImageError
from directory.util import Util
import os


class FactoryError(ValueError):
    def __init__(self, message: str):
        super().__init__(message)


class Factory:
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
        item.date = e.created
        if item.hash != e.hash:
            raise FactoryError(f"Hash mismatch for {e.name}")
        item.id = e.meta.id

        return item

    @staticmethod
    def from_directory_item(path: str, st: os.stat_result):
        try:
            return Factory.__image_from_directory_item(path, st)
        except InvalidImageError:
            pass

        try:
            return Factory.__video_from_directory_item(path, st)
        except InvalidVideoError:
            pass

        raise FactoryError(f"Path {path} is neither image nor video")

    @staticmethod
    def __image_from_directory_item(path: str, st: os.stat_result) -> Image:
        image = Image()
        image.full_path = path
        image.date = st.st_mtime
        image.size = st.st_size
        image.checksum = Util.checksum(path)
        return image

    @staticmethod
    def __video_from_directory_item(path: str, st: os.stat_result) -> Video:
        video = Video()
        video.full_path = path
        video.date = st.st_mtime
        video.size = st.st_size
        video.checksum = Util.checksum(path)
        return video
