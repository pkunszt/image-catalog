import hashlib
import os
from typing import Callable


class DirectoryUtil:

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
    def check_that_this_is_a_directory(directory_name) -> None:
        # check that the name given is indeed a directory
        if not os.path.isdir(directory_name):
            raise NotADirectoryError(directory_name + " is not a directory!")
