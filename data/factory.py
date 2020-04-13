from data.video import Video
from data.image import Image, InvalidImageError


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
            raise InvalidImageError(f"Entry mismatch, wrong kind {e.kind} found for: {e.name}; id:{e.meta.id}")

        item.name = e.name
        if e.type != item.type:
            raise InvalidImageError(f"Type mismatch for {e.name}")
        item.path = e.path
        item.size = e.size
        item.checksum = e.checksum
        item.date = e.created
        if item.hash != e.hash:
            raise InvalidImageError(f"Hash mismatch for {e.name}")
        item.id = e.meta.id

        return item
