import time
from unittest import TestCase
from typing import List, Generator
from elastic.connection import Connection
from elastic.delete import Delete
from elastic.index import Index
from elastic.retrieve import Retrieve
from elastic.store import Store
from directory.read import Reader


class TestStorage(TestCase):
    sorted_list: List
    testIndex: Index
    testDirectory = '../testfiles'
    connection: Connection

    def setUp(self) -> None:
        time.sleep(1)
        test_directory = Reader()
        test_directory.read(self.testDirectory)
        self.sorted_list = test_directory.file_list

        self.connection = Connection()
        reader = Retrieve(self.connection)
        deleter = Delete(self.connection)
        self.testIndex = Index()
        self.testIndex.image = 'test_unit_elastic_storage'
        self.testIndex.video = 'test_unit_elastic_storage'

        for _id in reader.all_ids(self.testIndex.image):
            deleter.delete_id(self.testIndex.image, _id)
        time.sleep(1)

    def get_elastic_storage(self, allow_duplicates: bool = False):
        elastic_storage = Store(self.connection.get(), index=self.testIndex, allow_duplicates=allow_duplicates)
        return elastic_storage

    def test_store_image_list(self):
        elastic_storage = self.get_elastic_storage()
        self.assertEqual(elastic_storage.image_list(item for item in self.sorted_list), 4)
        # When trying again, none will be stored - they are already there
        time.sleep(1)
        self.assertEqual(elastic_storage.image_list(item for item in self.sorted_list), 0)

    def test_store_video_list(self):
        elastic_storage = self.get_elastic_storage()
        self.assertEqual(elastic_storage.video_list(item for item in self.sorted_list), 1)
        # When trying again, none will be stored - they are already there
        time.sleep(1)
        self.assertEqual(elastic_storage.video_list(item for item in self.sorted_list), 0)

    def test_delete_by_id_list(self):
        elastic_storage = self.get_elastic_storage()
        self.assertEqual(elastic_storage.image_list(item for item in self.sorted_list), 4)
        time.sleep(1)
        id_list = []
        reader = Retrieve(self.connection)
        for _id in reader.all_ids(self.testIndex.image):
            id_list.append(_id)
        should = len(id_list)
        print(id_list)
        count = 0
        if should > 0:
            deleter = Delete(self.connection)
            count = deleter.delete_id_list(self.testIndex.image, id_list)
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
        self.assertEqual(elastic_storage.image_list(item for item in self.sorted_list), 4)
        time.sleep(1)
        reader = Retrieve(self.connection)
        for path in reader.all_paths(self.testIndex.image):
            self.assertEqual(path, self.testDirectory)

    def test_scan_index(self):
        elastic_storage = self.get_elastic_storage()
        self.assertEqual(elastic_storage.image_list(item for item in self.sorted_list), 4)
        time.sleep(1)
        reader = Retrieve(self.connection)
        l = [entry for entry in reader.all_ids(self.testIndex.image)]
        self.assertEqual(len(l), 4)

    def test_update(self):
        elastic_storage = self.get_elastic_storage()
        self.assertEqual(elastic_storage.image_list(item for item in self.sorted_list), 4)
        time.sleep(1)
        new_entries = {}
        i = 0
        reader = Retrieve(self.connection)
        for entry in reader.all_entries(self.testIndex.image):
            newname = 'image{0}'.format(i)
            change = {'name': newname, 'size': 1000+i}
            elastic_storage.update(change, entry.meta.id, entry.kind)
            new_entries[entry.meta.id] = change
            i = i + 1

        time.sleep(1)
        for entry in reader.all_entries(self.testIndex.image):
            self.assertEqual(entry.name, new_entries[entry.meta.id]['name'])
            self.assertEqual(entry.size, new_entries[entry.meta.id]['size'])
