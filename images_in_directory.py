import hashlib
import json
import os
import sys
from typing import List
from entry import Entry

from directory_util import DirectoryUtil


class ImagesInDirectory:
    """Class to scan a directory and return a list of files with all attributes set"""
    __file_list: List[Entry]
    __invalid_types_found: set
    __valid_types_found: set

    def __init__(self, directory_name: str = None):
        self.__file_list = []
        self.__invalid_types_found = set()
        self.__valid_types_found = set()
        if directory_name is not None:
            self.scan(directory_name)

    def scan(self, directory_name: str) -> List[Entry]:
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
                    self.__add_entry(util, item.path, item.stat())

        return self.__file_list

    def __add_image(self, util: DirectoryUtil, path: str, st: os.stat_result) -> bool:
        from image import Image, InvalidImageError
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

    def __add_video(self, util: DirectoryUtil, path: str, st: os.stat_result) -> bool:
        from video import Video, InvalidVideoError
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

    def __add_entry(self, util: DirectoryUtil, path: str, st: os.stat_result):
        if not self.__add_image(util, path, st):
            if not self.__add_video(util, path, st):
                from entry import Entry
                entry = Entry()
                entry.full_path = path
                self.__invalid_types_found.add(entry.type)

    def get_invalid_types_found(self) -> set:
        """Return the set of invalid types found, ie files that have not been processed"""
        return self.__invalid_types_found

    def get_valid_types_found(self) -> set:
        """Return the set of valid types found, ie file types that have been processed"""
        return self.__valid_types_found

    def get_file_list(self) -> List[Entry]:
        """Return the file list, same as return value from scan_directory"""
        return self.__file_list

    def get_file_list_as_dict(self) -> List[dict]:
        """Return the file list, same as return value from scan_directory"""
        return [
            item.to_dict()
            for item in self.__file_list
        ]


if __name__ == '__main__':
    image_dir = ImagesInDirectory(sys.argv[1])
    image_list = image_dir.get_file_list_as_dict()
    print(json.dumps(image_list, indent=4))
    if len(image_dir.get_invalid_types_found()) > 0:
        print("Invalid file types found:")
        print(image_dir.get_invalid_types_found())
