import json
import os
import time
from unittest import TestCase
from typing import List

from constants import TestConstants
from data import Factory
from elastic.connection import Connection
from elastic.delete import Delete
from elastic.retrieve import Retrieve
from elastic.store import Store
from data.directory import Folder
from data.image import Image


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

    def test_set_name(self):
        image = Image()
        image.full_path = "/some/path/name is a string.jpg"
        image.size = 1234
        image.modified = TestConstants.modified_test
        self.assertEqual(image.modified_time_str, TestConstants.modified_test_str)

        # Test that an image without captured date retains its name if we want to change only by captured date
        doc = image.to_dict()
        Store.set_name(doc, image, name_from_captured_date=True,
                       name_from_modified_date=False,
                       keep_manual_names=False)
        self.assertEqual(doc['name'], image.name)

        # An image without captured date but with modified date changes name if we want to change by mod date
        doc = image.to_dict()
        Store.set_name(doc, image, name_from_captured_date=False,
                       name_from_modified_date=True,
                       keep_manual_names=False)
        self.assertEqual(doc['name'], TestConstants.modified_test_str + '@' + image.name)

        # If the image has a meaningful name, modified date is not prepended if we want to keep manual names
        doc = image.to_dict()
        Store.set_name(doc, image, name_from_captured_date=False,
                       name_from_modified_date=True,
                       keep_manual_names=True)
        self.assertEqual(doc['name'], image.name)

        # If image has no meaningful name, then modified time IS prepended also if we want to keep manual names
        image.name = "IMG324342.jpg"
        doc = image.to_dict()
        Store.set_name(doc, image, name_from_captured_date=False,
                       name_from_modified_date=True,
                       keep_manual_names=True)
        self.assertEqual(doc['name'], TestConstants.modified_test_str + '@' + image.name)
        image.name = "name is a string.jpg"

        # add now captured date
        image.captured = TestConstants.captured_test
        self.assertEqual(image.captured_str, TestConstants.captured_test_str)

        # if we have a captured date and want to change by it, the whole name is changed
        doc = image.to_dict()
        Store.set_name(doc, image, name_from_captured_date=True,
                       name_from_modified_date=False,
                       keep_manual_names=False)
        self.assertEqual(doc['name'], TestConstants.captured_test_str + '.' + doc['type'])

        # if we want to change by modified name, but we do have captured date, also then captured date is set
        doc = image.to_dict()
        Store.set_name(doc, image, name_from_captured_date=False,
                       name_from_modified_date=True,
                       keep_manual_names=False)
        self.assertEqual(doc['name'], TestConstants.captured_test_str + '.' + doc['type'])

        # if we have some meaningful name, and want to keep it, the captured date is appended to it
        doc = image.to_dict()
        name, ext = os.path.splitext(doc['name'])
        Store.set_name(doc, image, name_from_captured_date=False,
                       name_from_modified_date=False,
                       keep_manual_names=True)
        self.assertEqual(doc['name'], name + ' ' + TestConstants.captured_test_str + ext)

        # if the name is not meaningful, replace it with the captured date even if not asked for
        image.name = "IMG324342.jpg"
        doc = image.to_dict()
        name, ext = os.path.splitext(doc['name'])
        Store.set_name(doc, image, name_from_captured_date=False,
                       name_from_modified_date=False,
                       keep_manual_names=True)
        self.assertEqual(doc['name'], TestConstants.captured_test_str + ext)

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
