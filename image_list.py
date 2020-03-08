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
                                     path=self.get_path_only(item.path),
                                     size=st.st_size,
                                     created=st.st_birthtime,
                                     checksum=self.checksum(item.path),
                                     type=image_type,
                                     kind=image_kind)   # 0 for images, 1 for videos
                    self.file_list.append(file_item)

        return self.file_list

    @staticmethod
    def checksum(filename):
        """Return the hex representation of the checksum on the full binary using blake2b. Needs full path."""
        file_hash = hashlib.blake2b()
        with open(filename, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                file_hash.update(chunk)
        return file_hash.hexdigest()

    def get_kind(self, image_type):
        """Depending on known extensions, return 0 for images, 1 for videos and -1 for unknown"""
        if image_type in self.image_types:
            return 0
        if image_type in self.video_types:
            return 1
        self.invalid_types_found.add(image_type)
        return -1

    @staticmethod
    def get_file_type(filename):
        """Given a file name return the extension as its type."""
        extension_start = filename.rfind('.')
        if extension_start != -1:
            file_type = filename[extension_start + 1:].lower()
        else:
            file_type = ''

        return file_type

    def get_invalid_types_found(self):
        """Return the set of invalid types found, ie files that have not been processed"""
        return self.invalid_types_found

    def get_file_list(self):
        """Return the file list, same as return value from scan_directory"""
        return self.file_list

    @staticmethod
    def get_path_only(file_name):
        """Just keep the path of the file name, dis"""
        last_slash = file_name.rfind('/')
        if last_slash < 0:
            return ""
        return file_name[0:last_slash]
