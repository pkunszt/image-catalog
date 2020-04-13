import os
import argparse
import re

import elastic
import data

class DeduplicateDirectories:
    __storage: Connection
    __recursive: bool
    __image_id_list: list
    __video_id_list: list
    __index: str
    __duplicates_to_delete: list
    __paths: list
    __date_pattern = re.compile(r'\d{4}-\d\d-\d\d \d\d-\d\d-\d\d\.\w+')         # regex for date format

    def __init__(self, host: str = 'localhost', port: int = 9200, index: str = None):
        if not host:
            host = 'localhost'
        if not port:
            port = 9200
        if index is not None:
            self.__index = index
        self.__storage = Connection(host, port)
        self.__count = 0
        self.__duplicates_to_delete = []

    def find_duplicate_images(self, directory_name: str):
        """Finding duplicate images per directory and returning a list of found duplicates.

        Arguments:
        directory_name -- name of the full path of the directory
        """
        self.__find_duplicates(directory_name)

    def find_duplicate_videos(self, directory_name: str):
        """Finding duplicate images per directory and returning a list of found duplicates.

        Arguments:
        directory_name -- name of the full path of the directory
        """
        self.__find_duplicates(directory_name, True)

    def __find_duplicates(self, directory_name, video: bool = False):
        self.__storage.clear_duplicate_list()
        self.__duplicates_to_delete.clear()
        self.__storage.build_duplicate_list_from_checksum(directory_filter=directory_name, video=video)
        for image_id_list in self.__storage.get_found_duplicate_ids():
            image_list = []
            for image_id in image_id_list:
                if not video:
                    item = self.__storage.get_image_by_id(image_id)
                else:
                    item = self.__storage.get_video_by_id(image_id)
                item['id'] = image_id
                image_list.append(item)
                print(item['name'], end=" ; ")

            # select the name to keep, add rest to deletion list
            to_keep = self.select_name_to_keep(image_list)
            for to_delete in image_list:
                if to_delete['id'] != to_keep['id']:
                    self.__duplicates_to_delete.append(to_delete)
            print("Keeping: {0}".format(os.path.join(to_keep['path'], to_keep['name'])))

    def select_name_to_keep(self, image_list) -> dict:
        for im in image_list:
            if self.check_date_name(im['name']):
                return im
        return sorted(image_list, key=lambda entry: entry['name'])[0]

    def check_date_name(self, name) -> bool:
        if self.__date_pattern.match(name):
            return True
        return False

    def get_image_id_list(self) -> list:
        return self.__image_id_list

    def get_video_id_list(self) -> list:
        return self.__video_id_list

    def get_image_by_id(self, image_id: str):
        return self.__storage.get_image_by_id(image_id)

    def delete_duplicates(self, video: bool = False):
        for item in self.__duplicates_to_delete:
            os.remove(os.path.join(item['path'], item['name']))
            if not video:
                self.__storage.id(self.__storage.image_index, item['id'])
            else:
                self.__storage.id(self.__storage.video_index, item['id'])

    def get_all_paths(self, video: bool = False):
        return self.__storage.all_paths(video)


def deduplicate_images_directory(dirname):
    deduplicate.find_duplicate_images(dirname)
    if not args.printonly:
        deduplicate.delete_duplicates()


def deduplicate_videos_directory(dirname):
    deduplicate.find_duplicate_videos(dirname)
    if not args.printonly:
        deduplicate.delete_duplicates(video=True)


    def clear_exact_duplicates_from_index(self, video: bool = False, dry_run: bool = True) -> int:
        count = 0
        index = self.get_index(video)
        self.build_duplicate_list_from_full_content(video)
        for hash_val, array_of_ids in self.__duplicate_dict.items():
            if len(array_of_ids) > 1:
                if not dry_run:
                    self.id_list(index, array_of_ids[1:])
                count = count + len(array_of_ids) - 1

        return count


    def build_duplicate_list_from_full_content(self, video: bool = False) -> None:
        for entry in self.scan_index(video=video):
            self.__duplicate_dict.setdefault(entry.hash, []).append(entry.meta.id)

    def build_duplicate_list_from_checksum(self, directory_filter: str = None,
                                           video: bool = False) -> None:
        for entry in self.scan_index(video=video, directory_filter=directory_filter):
            self.__duplicate_dict.setdefault(entry.checksum+entry.path, []).append(entry.meta.id)

    def clear_duplicate_list(self):
        if self.__duplicate_dict is None:
            self.__duplicate_dict = dict()
        self.__duplicate_dict.clear()

    def get_found_duplicate_ids(self) -> list:
        result = []
        for hash_val, array_of_ids in self.__duplicate_dict.items():
            if len(array_of_ids) > 1:
                result.append(array_of_ids)  # get last element of list

        return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Deduplicate images in the same directory')
    parser.add_argument('--dirname', '-d', type=str, help='name of directory to do deduplication in')
    parser.add_argument('--delete', action='store_true', help='really delete, not just print. Default: false')
    parser.add_argument('--host', type=str, help='the host where elastic runs. Default: localhost')
    parser.add_argument('--port', type=int, help='the port where elastic runs. Default: 9200')
    parser.add_argument('--index', type=str, help='the index in elastic. Defauls to ''catalog''')
    args = parser.parse_args()

    connection = elastic.Connection(args.host, args.port)
    if args.index is not None:
        connection.index = args.index
    store = elastic.Store(connection)

    deduplicate = DeduplicateDirectories(args.host, args.port)

    if args.dirname is not None:
        if not args.videos:
            deduplicate_images_directory(args.dirname)
        else:
            deduplicate_videos_directory(args.dirname)
    else:
        i = 0
        for p in deduplicate.get_all_paths(args.videos):
            print(p)
            if not args.videos:
                deduplicate_images_directory(p)
            else:
                deduplicate_videos_directory(p)
            i = i + 1
            if i > 10:
                break
