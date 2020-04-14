import time
from unittest import TestCase
from typing import List, Generator
from elastic.connection import Connection
from elastic.delete import Delete
from elastic.retrieve import Retrieve
from elastic.store import Store
from directory.read import Reader


class TestStorage(TestCase):
    file_list: List
    testIndex = 'test_unit_elastic_storage'
    testDirectory = '../testfiles'
    connection: Connection

    def setUp(self) -> None:
        time.sleep(1)
        test_directory = Reader()
        test_directory.read(self.testDirectory)
        self.file_list = test_directory.file_list

        self.connection = Connection()
        self.connection.index = self.testIndex

        # clean out test index
        reader = Retrieve(self.connection)
        deleter = Delete(self.connection)

        for _id in reader.all_ids():
            deleter.id(_id)
        time.sleep(1)

    def test_store_list(self):
        elastic_storage = Store(self.connection)
        self.assertEqual(elastic_storage.list(item for item in self.file_list), len(self.file_list))
        # When trying again, none will be stored - they are already there
        time.sleep(1)
        self.assertEqual(elastic_storage.list(item for item in self.file_list), 0)

    def test_delete_by_id_list(self):
        elastic_storage = Store(self.connection)
        self.assertEqual(elastic_storage.list(item for item in self.file_list), len(self.file_list))
        time.sleep(1)
        reader = Retrieve(self.connection)
        id_list = [ide for ide in reader.all_ids()]
        should = len(id_list)
        print(id_list)
        count = 0
        if should > 0:
            deleter = Delete(self.connection)
            count = deleter.id_list(id_list)
        self.assertEqual(count, should)

    def test_clear_exact_duplicates(self):
        elastic_storage = Store(self.connection, allow_duplicates=True)
        self.assertEqual(elastic_storage.list(item for item in self.file_list), len(self.file_list))
        self.assertEqual(elastic_storage.list(item for item in self.file_list), len(self.file_list))

        time.sleep(1)
        count = elastic_storage.clear_exact_duplicates_from_index(dry_run=False)
        self.assertEqual(count, 5)

    def test_build_duplicate_list_from_checksum(self):
        elastic_storage = Store(self.connection)
        self.assertEqual(elastic_storage.list(item for item in self.file_list), len(self.file_list))
        time.sleep(1)
        elastic_storage.build_duplicate_list_from_checksum(directory_filter=self.testDirectory)
        names = []
        for image_ids in elastic_storage.get_found_duplicate_ids():
            for image_id in image_ids:
                image = elastic_storage.get_id(image_id)
                names.append(image['name'])
                self.assertEqual(image['path'], self.testDirectory)
        self.assertTrue('spidey.jpeg' in names)
        self.assertTrue('spiderman.jpg' in names)
        pass

    def test_all_paths(self):
        elastic_storage = Store(self.connection)
        self.assertEqual(elastic_storage.list(item for item in self.file_list), len(self.file_list))
        time.sleep(1)
        reader = Retrieve(self.connection)
        for path in reader.all_paths():
            self.assertEqual(path, self.testDirectory)

    def test_scan_index(self):
        elastic_storage = Store(self.connection)
        self.assertEqual(elastic_storage.list(item for item in self.file_list), len(self.file_list))
        time.sleep(1)
        reader = Retrieve(self.connection)
        l = [entry for entry in reader.all_ids()]
        self.assertEqual(len(l), len(self.file_list))

    def test_update(self):
        elastic_storage = Store(self.connection)
        self.assertEqual(elastic_storage.list(item for item in self.file_list), len(self.file_list))
        time.sleep(1)
        new_entries = {}
        i = 0
        reader = Retrieve(self.connection)
        for entry in reader.all_entries():
            newname = 'image{0}'.format(i)
            change = {'name': newname, 'size': 1000+i}
            elastic_storage.update(change, entry.meta.id)
            new_entries[entry.meta.id] = change
            i = i + 1

        time.sleep(1)
        for entry in reader.all_entries():
            self.assertEqual(entry.name, new_entries[entry.meta.id]['name'])
            self.assertEqual(entry.size, new_entries[entry.meta.id]['size'])
