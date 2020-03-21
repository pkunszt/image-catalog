import hashlib
import os
from stat import S_ISDIR
from typing import Callable


class DirectoryUtil:
    image_types = {'png', 'jpg', 'jpeg', 'jpg2', 'jp2', 'heic', 'bmp', 'gif', 'orf', 'nef'}
    video_types = {'mov', 'avi', 'mp4', 'mpg', 'm4v'}

    def __init__(self):
        pass

    @staticmethod
    def checksum(filename: str) -> str:
        """Return the hex representation of the checksum on the full binary using blake2b. Needs full path."""
        file_hash = hashlib.blake2b()
        with open(filename, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                file_hash.update(chunk)
        return file_hash.hexdigest()

    @staticmethod
    def get_file_type(filename: str) -> str:
        """Given a file name return the extension as its type, in lowercase."""
        extension_start = filename.rfind('.')
        if extension_start != -1:
            file_type = filename[extension_start + 1:].lower()
        else:
            file_type = ''

        return file_type

    @staticmethod
    def get_path_only(filename: str) -> str:
        """Just keep the path of the file name, dis"""
        last_slash = filename.rfind('/')
        if last_slash < 0:
            return ""
        return filename[0:last_slash]

    def get_kind(self, image_type: str, unknown_callback: Callable[[str], None] = None) -> int:
        """Depending on known extensions, return 0 for images, 1 for videos and -1 for unknown.
        For Unknown there is an optional callback that can be executed with the image_type as argument."""
        if image_type.lower() in self.image_types:
            return 0
        if image_type.lower() in self.video_types:
            return 1
        if unknown_callback is not None:
            unknown_callback(image_type)
        return -1

    @staticmethod
    def check_that_this_is_a_directory(directory_name) -> None:
        mode: int = os.stat(directory_name).st_mode

        # check that the name given is indeed a directory
        if not S_ISDIR(mode):
            raise NotADirectoryError(directory_name + " is not a directory!")

