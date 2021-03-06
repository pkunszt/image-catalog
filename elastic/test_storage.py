import json
import os
import time
from unittest import TestCase
from typing import List

from data import Factory
from elastic.connection import Connection
from elastic.delete import Delete
from elastic.retrieve import Retrieve
from elastic.store import Store
from data.directory import Folder


class TestStorage(TestCase):
    file_list: List
    testIndex = 'test_unit_elastic_storage'
    testDirectory = '../testfiles'
    connection: Connection

    def setUp(self) -> None:
        test_directory = Folder()
        test_directory.read(self.testDirectory)
        self.file_list = test_directory.file_list

        self.connection = Connection()
        self.connection.index = self.testIndex

        # clean out test index
        reader = Retrieve(self.connection)
        deleter = Delete(self.connection)

        deleter.id_list([i for i in reader.all_ids()])
        time.sleep(1)

    def test_store_list(self):
        elastic_storage = Store(self.connection)
        stored = elastic_storage.list((item for item in self.file_list), keep_manual_names=True,
                                      destination_folder="/ImageCatalog/2000")
        print(json.dumps(stored, indent=4))
        self.assertEqual(len(stored), len(self.file_list) - 1)  # one less because we have one exact duplicate.
        # When trying again, none will be stored - they are already there
        self.assertEqual(len(elastic_storage.list(item for item in self.file_list)), 0)

    def test_delete_by_id_list(self):
        elastic_storage = Store(self.connection)
        self.assertEqual(len(elastic_storage.list(item for item in self.file_list)), len(self.file_list) - 1)
        time.sleep(1)
        reader = Retrieve(self.connection)
        id_list = [ide for ide in reader.all_ids()]
        should = len(id_list)
        count = 0
        if should > 0:
            deleter = Delete(self.connection)
            count = deleter.id_list(id_list)
        self.assertEqual(count, should)

    def test_all_paths(self):
        elastic_storage = Store(self.connection)
        self.assertEqual(len(elastic_storage.list(item for item in self.file_list)), len(self.file_list) - 1)
        time.sleep(1)
        reader = Retrieve(self.connection)
        for path in reader.all_paths():
            self.assertEqual(path, self.testDirectory)

    def test_scan_index(self):
        elastic_storage = Store(self.connection)
        self.assertEqual(len(elastic_storage.list(item for item in self.file_list)), len(self.file_list) - 1)
        time.sleep(1)
        reader = Retrieve(self.connection)
        lst = [entry for entry in reader.all_ids()]
        self.assertEqual(len(lst), len(self.file_list) - 1)

    def test_update(self):
        elastic_storage = Store(self.connection)
        self.assertEqual(len(elastic_storage.list(item for item in self.file_list)), len(self.file_list) - 1)
        time.sleep(1)
        new_entries = {}
        i = 0
        reader = Retrieve(self.connection)
        for entry in reader.all_entries():
            new_name = f'image{i}'
            change = {'name': new_name, 'size': 1000+i}
            elastic_storage.update(change, entry.meta.id)
            new_entries[entry.meta.id] = change
            i = i + 1

        time.sleep(1)
        for entry in reader.all_entries():
            self.assertEqual(entry.name, new_entries[entry.meta.id]['name'])
            self.assertEqual(entry.size, new_entries[entry.meta.id]['size'])

    def test_store_captured_name(self):
        elastic_storage = Store(self.connection)
        self.assertEqual(len(elastic_storage.list((item for item in self.file_list), name_from_captured_date=True)),
                         len(self.file_list) - 1)
        time.sleep(1)
        reader = Retrieve(self.connection)
        for item in reader.all_entries():
            entry = Factory.from_elastic_entry(item)
            if hasattr(entry, "captured"):
                self.assertEqual(os.path.splitext(entry.name)[0], entry.captured_str)

    def test_get_name(self):
        new_list = []
        for item in self.file_list:
            n, e = os.path.splitext(item.name)
            item.name = "item" + e
            new_list.append(item)
        elastic_storage = Store(self.connection)
        self.assertEqual(len(elastic_storage.list((item for item in new_list),
                                                  name_from_captured_date=True,
                                                  keep_manual_names=True)),
                         len(self.file_list) - 1)
