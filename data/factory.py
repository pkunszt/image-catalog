from data.video import Video, InvalidVideoError
from data.image import Image, InvalidImageError
import os
import hashlib


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
        return image

    @staticmethod
    def __video_from_directory_item(path: str) -> Video:
        video = Video()
        Factory.__entry_from_directory_item(video, path)
        return video

    @staticmethod
    def __entry_from_directory_item(e, path: str):
        e.full_path = path
        st = os.stat(path)
        e.date = st.st_mtime
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
