import os
from typing import List, Generator
from directory.util import Util
from data.factory import Factory, FactoryError
from data.entry import Entry


class Reader:
    """Class to scan a directory and return a list of entries, either image or video"""
    __file_list: List[Entry]
    __invalid_types_found: set
    __valid_types_found: set

    def __init__(self):
        self.__file_list = []
        self.__invalid_types_found = set()
        self.__valid_types_found = set()

    def read(self, directory_name: str) -> None:
        """Read from a given directory all image and video files.
        The result can be retrieved as a list of data.entry objects,
        as a list of dictionary objects or as the generator with all entries.
        Entries are images or videos, according to data.image and data.video

        Argument:
        directory_name -- name of the full path of the directory to scan.
        """
        Util.check_that_this_is_a_directory(directory_name)
        self.__file_list.clear()

        # scan the directory: fetch all data for files
        with os.scandir(directory_name) as iterator:
            for item in iterator:
                if not item.name.startswith('.') and item.is_file():
                    self.__add_entry(item.path, item.stat())

    def __add_entry(self, path: str, st: os.stat_result) -> None:
        """Adding an entry, specificity based on whether it is an image or a video. Args stat and path."""
        try:
            item = Factory.from_directory_item(path, st)
            self.__file_list.append(item)
            self.__valid_types_found.add(item.type)
        except FactoryError:
            self.__invalid_types_found.add(os.path.splitext(path.lower())[1])

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
        """Return the list of entries, these will be either Video or Image objects"""
        return self.__file_list

    @property
    def files(self) -> Generator:
        """Return the list as a generator to be iterated through"""
        return (
            entry
            for entry in self.__file_list
        )

    def file_list_as_dict(self) -> List[dict]:
        """Return the list of entries as dictionary objects, to be used in JSON"""
        return [
            entry.to_dict()
            for entry in self.__file_list
        ]
