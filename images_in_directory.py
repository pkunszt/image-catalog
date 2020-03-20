import json
import os
import sys
from stat import *
from typing import List

from directory_util import DirectoryUtil


class ImagesInDirectory:
    """Class to scan a directory and return a list of files with all attributes set"""
    __file_list: List[dict]
    invalid_types_found: set

    def __init__(self, directory_name: str = None):
        self.__file_list = []
        self.invalid_types_found = set()
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
        mode: int = os.stat(directory_name).st_mode
        util = DirectoryUtil()

        # check that the name given is indeed a directory
        if not S_ISDIR(mode):
            raise NotADirectoryError(directory_name + " is not a directory!")

        # scan the directory: fetch all data for files
        with os.scandir(directory_name) as iterator:
            for item in iterator:
                if not item.name.startswith('.') and item.is_file():
                    st = item.stat()
                    image_type = util.get_file_type(item.name)
                    image_kind = util.get_kind(image_type, self.__add_invalid_type)
                    if image_kind < 0:
                        continue
                    file_item = dict(name=item.name,
                                     path=util.get_path_only(item.path),
                                     size=st.st_size,
                                     created=st.st_birthtime,
                                     checksum=util.checksum(item.path),
                                     type=image_type,
                                     kind=image_kind)   # 0 for images, 1 for videos
                    self.__file_list.append(file_item)

        return self.__file_list

    def __add_invalid_type(self, image_type: str) -> None:
        self.invalid_types_found.add(image_type)

    def get_invalid_types_found(self) -> set:
        """Return the set of invalid types found, ie files that have not been processed"""
        return self.invalid_types_found

    def get_file_list(self) -> List[dict]:
        """Return the file list, same as return value from scan_directory"""
        return self.__file_list


if __name__ == '__main__':
    image_dir = ImagesInDirectory(sys.argv[1])
    image_list = image_dir.get_file_list()
    print(json.dumps(image_list, indent=4))
