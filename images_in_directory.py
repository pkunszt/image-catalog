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
        entry = {'type': util.get_file_type(name)}
        entry['kind'] = util.get_kind(entry['type'], self.__add_invalid_type)
        if entry['kind'] >= 0:
            entry['name'] = name
            entry['path'] = util.get_path_only(path)
            entry['size'] = st.st_size
            entry['created'] = st.st_mtime
            entry['checksum'] = util.checksum(path)
            entry['hash'] = ImagesInDirectory.get_hash_from_entry(entry)

            self.__valid_types_found.add(entry['type'])
            self.__file_list.append(entry)

    @staticmethod
    def get_hash_from_entry(entry: dict) -> object:
        value = entry['name'] + entry['path'] + str(entry['size']) +\
                entry['checksum'] + str(entry['type']) + str(entry['kind'])
        return hashlib.md5(value.encode()).hexdigest()

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
