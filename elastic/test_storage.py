import time
from unittest import TestCase
from images_in_directory import ImagesInDirectory
from typing import List
from elastic.connection import Connection
from directory.read import Reader


class TestStorage(TestCase):
    sorted_list: List
    testIndex = 'test_unit_elastic_storage'
    testDirectory = '../testfiles'

    def setUp(self) -> None:
        time.sleep(1)
        test_directory = Reader()
        file_list = test_directory.read(self.testDirectory)
        self.sorted_list = sorted(file_list, key=lambda i: i.name)
        elastic_storage = Connection()
        for _id in elastic_storage.all_ids_in_index(self.testIndex):
            elastic_storage.delete_id(self.testIndex, _id)
        time.sleep(1)

    def get_elastic_storage(self, allow_duplicates: bool = False):
        elastic_storage = Connection(allow_duplicates=allow_duplicates)
        elastic_storage.image_index = self.testIndex
        elastic_storage.video_index = self.testIndex
        return elastic_storage

    def test_store_image_list(self):
        elastic_storage = self.get_elastic_storage()
        self.assertEqual(elastic_storage.store_image_list(self.sorted_list), 4)
        # When trying again, none will be stored - they are already there
        time.sleep(1)
        self.assertEqual(elastic_storage.store_image_list(self.sorted_list), 0)

    def test_store_video_list(self):
        elastic_storage = self.get_elastic_storage()
        self.assertEqual(elastic_storage.store_video_list(self.sorted_list), 1)
        # When trying again, none will be stored - they are already there
        time.sleep(1)
        self.assertEqual(elastic_storage.store_video_list(self.sorted_list), 0)

    def test_delete_by_id_list(self):
        elastic_storage = self.get_elastic_storage()
        self.assertEqual(elastic_storage.store_image_list(self.sorted_list), 4)
        time.sleep(1)
        id_list = []
        for _id in elastic_storage.all_ids_in_index(self.testIndex):
            id_list.append(_id)
        should = len(id_list)
        print(id_list)
        count = 0
        if should > 0:
            count = elastic_storage.delete_id_list(self.testIndex, id_list)
        self.assertEqual(count, should)

    def test_clear_exact_duplicates(self):
        elastic_storage = self.get_elastic_storage(allow_duplicates=True)
        self.assertEqual(elastic_storage.store_image_list(self.sorted_list), 4)
        self.assertEqual(elastic_storage.store_image_list(self.sorted_list), 4)
        self.assertEqual(elastic_storage.store_video_list(self.sorted_list), 1)

        time.sleep(1)
        count = elastic_storage.clear_exact_duplicates_from_index(dry_run=False)
        self.assertEqual(count, 4)

    def test_build_duplicate_list_from_checksum(self):
        elastic_storage = self.get_elastic_storage()
        self.assertEqual(elastic_storage.store_image_list(self.sorted_list), 4)
        time.sleep(1)
        elastic_storage.build_duplicate_list_from_checksum(directory_filter=self.testDirectory)
        names = []
        for image_ids in elastic_storage.get_found_duplicate_ids():
            for image_id in image_ids:
                image = elastic_storage.get_image_by_id(image_id)
                names.append(image['name'])
                self.assertEqual(image['path'], self.testDirectory)
        self.assertTrue('spidey.jpeg' in names)
        self.assertTrue('spiderman.jpg' in names)
        pass

    def test_all_paths(self):
        elastic_storage = self.get_elastic_storage()
        self.assertEqual(elastic_storage.store_image_list(self.sorted_list), 4)
        time.sleep(1)
        for path in elastic_storage.all_paths():
            self.assertEqual(path, self.testDirectory)

    def test_scan_index(self):
        elastic_storage = self.get_elastic_storage()
        self.assertEqual(elastic_storage.store_image_list(self.sorted_list), 4)
        time.sleep(1)
        for entry in elastic_storage.scan_index():
            print(entry.meta.id)

    def test_update(self):
        elastic_storage = self.get_elastic_storage()
        self.assertEqual(elastic_storage.store_image_list(self.sorted_list), 4)
        time.sleep(1)
        new_entries = {}
        i = 0
        for entry in elastic_storage.scan_index():
            print("name: {0}, id: {1}".format(entry.name, entry.meta.id))
            newname = 'image{0}'.format(i)
            change = {'name': newname, 'size': 1000+i}
            elastic_storage.update(change, entry.meta.id)
            new_entries[entry.meta.id] = change
            i = i + 1

        time.sleep(1)
        for entry in elastic_storage.scan_index():
            self.assertEqual(entry.name, new_entries[entry.meta.id]['name'])
            self.assertEqual(entry.size, new_entries[entry.meta.id]['size'])
