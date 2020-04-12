import os
import sys
from directory import Util


class ListAllFileTypes:
    """Class to scan a directory recursively and return a list of file types"""
    __valid_types_found: set
    util: Util

    def __init__(self, directory_name: str = None, recursive: bool = True):
        self.__invalid_types_found = set()
        self.__valid_types_found = set()
        self.util = Util()
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
        self.walktree(directory_name)

        return self.get_valid_types_found()

    def get_valid_types_found(self) -> set:
        """Return the set of valid types found, ie file types that have been processed"""
        return self.__valid_types_found

    def walktree(self, directory_name: str):
        # scan the directory: fetch all data for files
        with os.scandir(directory_name) as iterator:
            for item in iterator:
                if item.is_dir() and self.recurse:
                    self.walktree(item.path)
                if not item.name.startswith('.') and item.is_file():
                    self.__valid_types_found.add(os.path.splitext(item.name)[1])


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: " + sys.argv[0] + " dirname [recurse]")
        print("    dirname : name of directory to scan for file types")
        print("    recurse : recurse 0 or 1 (default 1 or true)")
    recurse: bool = True
    if len(sys.argv) >= 3 and (sys.argv[2] == 0 or sys.argv[2].lower() == "false"):
        recurse = False
    list_file_types = ListAllFileTypes(directory_name=sys.argv[1], recursive=recurse)
    type_list = list_file_types.get_valid_types_found()
    print(type_list)
