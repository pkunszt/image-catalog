import os
import argparse

from directory_util import DirectoryUtil
from elastic_storage import ElasticStorage
from images_in_directory import ImagesInDirectory


class AddToCatalog:
    __catalog: ElasticStorage
    recursive: bool
    count: int

    def __init__(self, host: str = 'localhost', port: int = 9200, allow_duplicates: bool = False):
        if not host:
            host = 'localhost'
        if not port:
            port = 9200
        self.__catalog = ElasticStorage(host, port, allow_duplicates=allow_duplicates)
        self.count = 0

    def load_from_directory(self, directory_name: str, recursive: bool = True):
        """Scanning a given directory for image and video files.
        Adds all found items to the catalog. By default it recurses into subdirs.

        Arguments:
        directory_name -- name of the full path of the directory to scan.
        recurse -- True by default, set to False to not recurse into subdirectories
        """
        DirectoryUtil.check_that_this_is_a_directory(directory_name)
        self.recursive = recursive
        self.walktree(directory_name)

        return self.count

    def walktree(self, directory_name: str):
        # scan the directory: fetch all data for files
        with os.scandir(directory_name) as iterator:
            for item in iterator:
                if item.is_dir() and self.recursive:
                    self.walktree(item.path)
        self.add_entries_in_directory(directory_name)

    def add_entries_in_directory(self, directory_name: str) -> None:
        image_list = ImagesInDirectory(directory_name)
        entry_list = image_list.get_file_list()
        self.count = self.count + self.__catalog.store_list(entry_list)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Catalog all image and video files in the given directory')
    parser.add_argument('dirname', type=str, help='name of directory to catalog')
    parser.add_argument('--recursive', '-r', action='store_true', help='recurse into subdirectories. Default: false')
    parser.add_argument('--allow_duplicates', '-d', action='store_true', help='Duplicates are not ok by default.')
    parser.add_argument('--host', type=str, help='the host where elastic runs. Default: localhost')
    parser.add_argument('--port', type=int, help='the port where elastic runs. Default: 9200')
    args = parser.parse_args()
    add_to_catalog = AddToCatalog(args.host, args.port, allow_duplicates=args.allow_duplicates)
    print(add_to_catalog.load_from_directory(args.dirname, args.recursive))
