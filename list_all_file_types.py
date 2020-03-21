import os
import sys
from typing import Callable
from directory_util import DirectoryUtil


class ListAllFileTypes:
    """Class to scan a directory recursively and return a list of file types"""
    __invalid_types_found: set
    __valid_types_found: set
    util: DirectoryUtil

    def __init__(self, directory_name: str = None, recursive: bool = True):
        self.__invalid_types_found = set()
        self.__valid_types_found = set()
        self.util = DirectoryUtil()
        self.recurse = recursive
        if directory_name is not None:
            self.scan(directory_name)

    def scan(self, directory_name: str) -> set:
        """Scanning a given directory for file types.
        Returns a set of file types found. By default it recurses into subdirs.

        Arguments:
        directory_name -- name of the full path of the directory to scan.
        recurse -- True by default, set to False to not recurse into subdirectories
        """
        self.util.check_that_this_is_a_directory(directory_name)
        self.walktree(directory_name, self.check_type)

        return self.get_list_of_found_types()

    def get_list_of_found_types(self) -> set:
        return self.__valid_types_found.union(self.__invalid_types_found)

    def __add_invalid_type(self, image_type: str) -> None:
        self.__invalid_types_found.add(image_type)

    def get_invalid_types_found(self) -> set:
        """Return the set of invalid types found, ie files that have not been processed"""
        return self.__invalid_types_found

    def get_valid_types_found(self) -> set:
        """Return the set of valid types found, ie file types that have been processed"""
        return self.__valid_types_found

    def walktree(self, directory_name: str, callback: Callable[[os.DirEntry], None]):
        # scan the directory: fetch all data for files
        with os.scandir(directory_name) as iterator:
            for item in iterator:
                if item.is_dir() and self.recurse:
                    self.walktree(item.path, callback)
                if not item.name.startswith('.') and item.is_file():
                    callback(item)

    def check_type(self, entry: os.DirEntry):
        image_type = self.util.get_file_type(entry.name)
        image_kind = self.util.get_kind(image_type, self.__add_invalid_type)
        if image_kind < 0:
            return
        self.__valid_types_found.add(image_type)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: " + sys.argv[0] + " dirname [recurse]")
        print("    dirname : name of directory to scan for file types")
        print("    recurse : recurse 0 or 1 (default 1 or true)")
    recurse: bool = True
    if len(sys.argv) >= 3 and (sys.argv[2] == 0 or sys.argv[2].lower() == "false"):
        recurse = False
    list_file_types = ListAllFileTypes(directory_name=sys.argv[1], recursive=recurse)
    type_list = list_file_types.get_list_of_found_types()
    print(type_list)
