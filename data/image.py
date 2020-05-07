from __future__ import annotations
from data.entry import Entry
from tools import Constants


class InvalidImageError(ValueError):
    def __init__(self, message: str):
        super().__init__(message)


class Image(Entry):
    """This is the image entry in the catalog."""

    def __init__(self):
        pass

    def __repr__(self):
        return str(self.to_dict())

    @property
    def kind(self):
        """Image kind is 1 by definition"""
        return Constants.IMAGE_KIND

    @Entry.name.setter
    def name(self, name):
        super(Image, self.__class__).name.fset(self, name)   # This is how to call a superclass setter
        if self.type not in Constants.image_types:
            raise InvalidImageError(f"Not an image with extension {self.type}")

    def diff(self, to: Image) -> dict:
        result = dict()
        me = self.to_dict()
        other = to.to_dict()
        for key in sorted(me.keys()):
            if key in other.keys() and me[key] != other[key]:
                result[key] = other[key]

        return result
