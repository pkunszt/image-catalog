import hashlib
import json
import os
import sys
from typing import List

from directory_util import DirectoryUtil


class ImagesInDirectory:
    """Class to scan a directory and return a list of files with all attributes set"""
    __file_list: List[dict]
    __invalid_types_found: set
    __valid_types_found: set

    def __init__(self, directory_name: str = None):
        self.__file_list = []
        self.__invalid_types_found = set()
        self.__valid_types_found = set()
        if directory_name is not None:
            self.scan(directory_name)

    def scan(self, directory_name: str) -> List[dict]:
        """Scanning a given directory for image and video files.
        Returns a list of dictionaries with an entry for each
        image or video file, containing:

        name -- the name of the file,
        path -- the full path to the file,
        size -- its size in bytes,
        created -- its created date in seconds,
        checksum -- its checksum using blake2b hash
        type -- basically the file ending
        kind -- 0 is image, 1 is video

        Argument:
        directory_name -- name of the full path of the directory to scan.
        """
        util = DirectoryUtil()
        util.check_that_this_is_a_directory(directory_name)

        # scan the directory: fetch all data for files
        with os.scandir(directory_name) as iterator:
            for item in iterator:
                if not item.name.startswith('.') and item.is_file():
                    self.__add_entry(util, item.name, item.path, item.stat())

        return self.__file_list

    def __add_entry(self, util: DirectoryUtil, name: str, path: str, st):

        entry_type = util.get_file_type(name)
        entry_kind = util.get_kind(entry_type, self.__add_invalid_type)
        if entry_kind >= 0:
            entry_name = name
            entry_path = util.get_path_only(path)
            entry_size = st.st_size
            entry_created = st.st_birthtime
            entry_checksum = util.checksum(path)
            value = entry_name + entry_path + str(entry_size) + entry_checksum + str(entry_type) + str(entry_kind)
            entry_hash = hashlib.md5(value.encode()).hexdigest()

            entry = dict(name=entry_name,
                         path=entry_path,
                         size=entry_size,
                         created=entry_created,
                         checksum=entry_checksum,
                         type=entry_type,
                         kind=entry_kind,
                         hash=entry_hash)

            self.__valid_types_found.add(entry_type)
            self.__file_list.append(entry)

    def __add_invalid_type(self, image_type: str) -> None:
        self.__invalid_types_found.add(image_type)

    def get_invalid_types_found(self) -> set:
        """Return the set of invalid types found, ie files that have not been processed"""
        return self.__invalid_types_found

    def get_valid_types_found(self) -> set:
        """Return the set of valid types found, ie file types that have been processed"""
        return self.__valid_types_found

    def get_file_list(self) -> List[dict]:
        """Return the file list, same as return value from scan_directory"""
        return self.__file_list


if __name__ == '__main__':
    image_dir = ImagesInDirectory(sys.argv[1])
    image_list = image_dir.get_file_list()
    print(json.dumps(image_list, indent=4))
    if len(image_dir.get_invalid_types_found()) > 0:
        print("Invalid file types found:")
        print(image_dir.get_invalid_types_found())
