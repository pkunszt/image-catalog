from __future__ import annotations
from data.entry import Entry
from constants import Constants


class InvalidVideoError(ValueError):
    def __init__(self, message: str):
        super().__init__(message)


class Video(Entry):
    """This is the video entry in the catalog."""

    def __init__(self):
        pass

    def __repr__(self):
        return str(self.to_dict())

    @property
    def kind(self):
        """Video kind is 2 by definition"""
        return Constants.VIDEO_KIND

    @Entry.name.setter
    def name(self, name):
        super(Video, self.__class__).name.fset(self, name)   # This is how to call a superclass setter
        if self.type not in Constants.video_types:
            raise InvalidVideoError(f"Not video with extension {self.type}")

    def diff(self, to: Video) -> dict:
        result = dict()
        me = self.to_dict()
        other = to.to_dict()
        for key in sorted(me.keys()):
            if key in other.keys() and me[key] != other[key]:
                result[key] = other[key]

        return result
