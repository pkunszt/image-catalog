import os
import datetime
import hashlib
import inspect
from constants import Constants


class EntryException(LookupError):
    def __init__(self, message: str):
        super().__init__(message)


class Entry:

    def __repr__(self):
        return "Entry"

    _id: str
    _name: str
    _path: str
    _dropbox_path: bool
    _catalog: bool
    _size: int
    _modified: int
    _type: str
    _checksum: str
    _captured: int
    _location: str
    _dimensions: str
    _duration: int
    _original_path: str

    date_time_format: str = "%Y-%m-%d %H-%M-%S"

    @property
    def name(self):
        return self._name

    @property
    def path(self):
        return self._path

    @property
    def dropbox_path(self):
        return self._dropbox_path if hasattr(self, "_dropbox_path") else False

    @property
    def catalog(self):
        return self._catalog if hasattr(self, "_catalog") else False

    @property
    def full_path(self):
        return os.path.join(self.path, self.name)

    @property
    def size(self):
        return self._size

    @property
    def modified(self):
        return self._modified

    @property
    def type(self):
        return self._type

    @property
    def checksum(self):
        return self._checksum

    @property
    def captured(self):
        return self._captured

    @property
    def captured_str(self):
        return datetime.datetime.fromtimestamp(self.captured / 1000.0) \
            .strftime(Entry.date_time_format)  # , tz=datetime.timezone(datetime.timedelta(hours=1))

    @property
    def modified_str(self):
        return datetime.date.fromtimestamp(self.modified / 1000.0).isoformat()

    @property
    def modified_time_str(self):
        return datetime.datetime.fromtimestamp(self.modified / 1000.0) \
            .strftime(Entry.date_time_format)  # , tz=datetime.timezone(datetime.timedelta(hours=1))

    @property
    def modified_ts(self):
        return datetime.datetime.fromtimestamp(self.modified / 1000.0)

    @property
    def path_hash(self):
        value = self.path + self.checksum
        return hashlib.md5(value.encode()).hexdigest()

    @property
    def hash(self):
        return type(self).hash_from_name(self.full_path)

    @staticmethod
    def hash_from_name(path):
        return hashlib.md5(path.encode()).hexdigest()

    @property
    def location(self):
        return self._location if hasattr(self, "_location") else None

    @location.setter
    def location(self, loc: str):
        self._location = loc

    def set_location_from_lat_lon(self, latitude: float, longitude: float):
        self._location = f"{round(latitude, 5)},{round(longitude, 5)}"

    @property
    def dimensions(self):
        return self._dimensions

    @dimensions.setter
    def dimensions(self, dimensions):
        self._dimensions = dimensions

    @property
    def duration(self):
        return self._duration

    @duration.setter
    def duration(self, c):
        self._duration = int(c)

    @name.setter
    def name(self, name: str):
        if name.find(os.path.sep) >= 0:
            raise EntryException(f"File name given must just be a name, not a path: {name}")
        base, image_type = os.path.splitext(name)
        self._name = name
        self._type = image_type.lower()[1:]

    @property
    def original_path(self):
        return self._original_path

    @path.setter
    def path(self, path: str):
        self._path = path

    @dropbox_path.setter
    def dropbox_path(self, flag: bool):
        self._dropbox_path = flag

    @catalog.setter
    def catalog(self, flag: bool):
        self._catalog = flag

    @full_path.setter
    def full_path(self, full_path):
        self.path, self.name = os.path.split(full_path)

    @size.setter
    def size(self, size: int):
        self._size = size

    @modified.setter
    def modified(self, modified: int):
        self._modified = int(modified)

    @captured.setter
    def captured(self, c):
        self._captured = int(c)

    @checksum.setter
    def checksum(self, checksum: str):
        self._checksum = checksum

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, i):
        self._id = i

    def save_path(self):
        self._original_path = self.full_path

    def to_dict(self):
        output = dict()
        for name, value in inspect.getmembers(self, lambda a: not (inspect.isroutine(a))):
            if name in Constants.attributes:
                if value:
                    output.update({name: value})
        return output

    def update(self, data: dict):
        for attr, value in data.items():
            setattr(self, attr, value)
        return self
