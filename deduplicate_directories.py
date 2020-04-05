import os
import argparse
import re

from elastic_storage import ElasticStorage


class DeduplicateDirectories:
    __storage: ElasticStorage
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
        self.__storage = ElasticStorage(host, port)
        self.__count = 0

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
        self.__duplicates_to_delete = []
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
            print("Selecting:", end=" ")
            to_delete = self.select_name(image_list)
            self.__duplicates_to_delete.append(to_delete)
            print(to_delete['name'])

    def select_name(self, image_list) -> dict:
        for i in image_list:
            if self.check_date_name(i['name']):
                return i
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
            os.remove(item['path']+'/'+item['name'])
            if not video:
                self.__storage.delete_id(self.__storage.image_index, item['id'])
            else:
                self.__storage.delete_id(self.__storage.video_index, item['id'])

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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Deduplicate images in the same directory')
    parser.add_argument('--dirname', '-d', type=str, help='name of directory to catalog')
    parser.add_argument('--videos', '-v', action='store_true', help='videos instead of images. Default: false')
    parser.add_argument('--printonly', '-p', action='store_false', help='don\'t delete, just print. Default: true')
    parser.add_argument('--host', type=str, help='the host where elastic runs. Default: localhost')
    parser.add_argument('--port', type=int, help='the port where elastic runs. Default: 9200')
    args = parser.parse_args()

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

