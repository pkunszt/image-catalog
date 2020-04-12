import os
from typing import List, Generator
from data import Entry
from directory.util import Util


class Reader:
    """Class to scan a directory and return a list of entries, either image or video"""
    __file_list: List[Entry]
    __invalid_types_found: set
    __valid_types_found: set

    def __init__(self, directory_name: str = None):
        self.__file_list = []
        self.__invalid_types_found = set()
        self.__valid_types_found = set()
        if directory_name is not None:
            self.read(directory_name)

    def read(self, directory_name: str):
        """Read from a given directory all image and video files.
        The result can be retrieved as a list of data.entry objects,
        as a list of dictionary objects or as the generator with all entries.
        Entries are images or videos, according to data.image and data.video

        Argument:
        directory_name -- name of the full path of the directory to scan.
        """
        util = Util()
        util.check_that_this_is_a_directory(directory_name)
        self.__file_list.clear()

        # scan the directory: fetch all data for files
        with os.scandir(directory_name) as iterator:
            for item in iterator:
                if not item.name.startswith('.') and item.is_file():
                    self.__add_entry(util, item.path, item.stat())

    def __add_image(self, util: Util, path: str, st: os.stat_result) -> bool:
        from data.image import Image, InvalidImageError
        try:
            image = Image()
            image.full_path = path
            image.date = st.st_mtime
            image.size = st.st_size
            image.checksum = util.checksum(path)
            self.__file_list.append(image)
            self.__valid_types_found.add(image.type)
            return True
        except InvalidImageError:
            return False

    def __add_video(self, util: Util, path: str, st: os.stat_result) -> bool:
        from data.video import Video, InvalidVideoError
        try:
            video = Video()
            video.full_path = path
            video.date = st.st_mtime
            video.size = st.st_size
            video.checksum = util.checksum(path)
            self.__file_list.append(video)
            self.__valid_types_found.add(video.type)
            return True
        except InvalidVideoError:
            return False

    def __add_entry(self, util: Util, path: str, st: os.stat_result):
        if not self.__add_image(util, path, st):
            if not self.__add_video(util, path, st):
                self.__invalid_types_found.add(os.path.splitext(path)[1])

    @property
    def invalid_types(self) -> set:
        """Return the set of invalid types found, ie files that have not been processed"""
        return self.__invalid_types_found

    @property
    def valid_types(self) -> set:
        """Return the set of valid types found, ie file types that have been processed"""
        return self.__valid_types_found

    @property
    def file_list(self) -> List[Entry]:
        """Return the file list, same as return value from scan_directory"""
        return self.__file_list

    @property
    def files(self) -> Generator:
        return (
            entry
            for entry in self.__file_list
        )

    def file_list_as_dict(self) -> List[dict]:
        """Return the file list, same as return value from scan_directory"""
        return [
            entry.to_dict()
            for entry in self.__file_list
        ]
