import os
import datetime
import hashlib


class EntryException(LookupError):
    def __init__(self, message: str):
        super().__init__(message)


class Entry:

    def __repr__(self):
        return "Entry"

    _name: str
    _path: str
    _size: int
    _date: int
    _type: str
    _checksum: str
    _id: str

    @property
    def name(self):
        return self._name

    @property
    def path(self):
        return self._path

    @property
    def full_path(self):
        return os.path.join(self.path, self.name)

    @property
    def size(self):
        return self._size

    @property
    def date(self):
        return self._date

    @property
    def type(self):
        return self._type

    @property
    def checksum(self):
        return self._checksum

    @property
    def date_str(self):
        return datetime.date.fromtimestamp(self.date).isoformat()

    @property
    def datetime_str(self):
        return datetime.datetime.fromtimestamp(self.date).strftime("%Y-%m-%d %H-%M-%S")

    @property
    def hash(self):
        value = self.name + self.path + str(self.size) +\
                self.checksum + str(self.type)
        return hashlib.md5(value.encode()).hexdigest()

    @name.setter
    def name(self, name: str):
        if name.find(os.path.sep) >= 0:
            raise EntryException(f"File name given must just be a name, not a path: {name}")
        base, image_type = os.path.splitext(name)
        self._name = name
        self._type = image_type.lower()[1:]

    @path.setter
    def path(self, path: str):
        self._path = path

    @full_path.setter
    def full_path(self, full_path):
        self.path, self.name = os.path.split(full_path)

    @size.setter
    def size(self, size: int):
        self._size = size

    @date.setter
    def date(self, date: int):
        self._date = int(date)

    @checksum.setter
    def checksum(self, checksum: str):
        self._checksum = checksum

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, _id):
        self._id = _id

    def to_dict(self):
        raise EntryException("to_dict called on base class Entry")
