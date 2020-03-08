import os
import hashlib
from stat import *


class ImageList:
    """Class to scan a directory and return a list of files with all attributes set"""
    image_types = {'png', 'jpg', 'jpeg', 'heic', 'bmp'}
    video_types = {'mov', 'avi', 'mp4'}

    def __init__(self):
        self.file_list = []
        self.invalid_types_found = set()

    def scan_directory(self, directory_name):
        mode: int = os.stat(directory_name).st_mode

        # check that the name given is indeed a directory
        if not S_ISDIR(mode):
            raise NotADirectoryError(directory_name + " is not a directory!")

        # scan the directory: fetch all data for files
        with os.scandir(directory_name) as iterator:
            for item in iterator:
                if not item.name.startswith('.') and item.is_file():
                    st = item.stat()
                    image_type = self.get_file_type(item.name)
                    image_kind = self.get_kind(image_type)
                    if image_kind < 0:
                        continue
                    file_item = dict(name=item.name,
                                     path=item.path,
                                     size=st.st_size,
                                     created=st.st_birthtime,
                                     checksum=self.checksum(item.path),
                                     type=image_type,
                                     kind=image_kind)   # 0 for images, 1 for videos
                    self.file_list.append(file_item)

        return self.file_list

    @staticmethod
    def checksum(filename):
        file_hash = hashlib.blake2b()
        with open(filename, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                file_hash.update(chunk)
        return file_hash.hexdigest()

    def get_kind(self, image_type):
        if image_type in self.image_types:
            return 0
        if image_type in self.video_types:
            return 1
        self.invalid_types_found.add(image_type)
        return -1

    @staticmethod
    def get_file_type(filename):
        extension_start = filename.rfind('.')
        if extension_start != -1:
            file_type = filename[extension_start + 1:].lower()
        else:
            file_type = ''

        return file_type

    def get_invalid_types_found(self):
        return self.invalid_types_found

    def get_file_list(self):
        return self.file_list
