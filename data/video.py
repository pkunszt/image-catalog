from __future__ import annotations
from data.entry import Entry


class InvalidVideoError(ValueError):
    def __init__(self, message: str):
        super().__init__(message)


class Video(Entry):
    """This is the video entry in the catalog."""

    __video_types = {'mov', 'avi', 'mp4', 'mpg', 'm4v'}

    def __init__(self):
        self.id = 0

    def __repr__(self):
        return str(self.to_dict())

    @property
    def kind(self):
        """Video kind is 0 by definition"""
        return 1

    @Entry.name.setter
    def name(self, name):
        super(Video, self.__class__).name.fset(self, name)   # This is how to call a superclass setter
        if self.type not in self.__video_types:
            raise InvalidVideoError(f"Not video with extension {self.type}")

    def to_dict(self):
        return dict(
            name=self.name,
            path=self.path,
            size=self.size,
            modified=self.modified,
            type=self.type,
            kind=self.kind,
            hash=self.hash,
            checksum=self.checksum
        )

    def diff(self, to: Video) -> dict:
        result = dict()
        me = self.to_dict()
        other = to.to_dict()
        for key in sorted(me.keys()):
            if key in other.keys() and me[key] != other[key]:
                result[key] = other[key]

        return result
