import os
import time
from unittest import TestCase
import sync_catalog_with_disk
from directory import Reader
from elastic import Store, Connection, Delete, Retrieve


class TestSyncCatalogWithDisk(TestCase):
    test_file = "testfile.mov"
    test_dir = "./testfiles"
    test_index = 'test_sync'
    test_path = os.path.join(test_dir, test_file)

    def test_sync(self):

        if not os.path.exists(self.test_path):
            file = open(self.test_path, 'w')
            file.writelines(["This is a testfile", "just some text, really"])
            file.close()

        test_directory = Reader()
        test_directory.read(self.test_dir)
        file_list = test_directory.file_list
        connection = Connection()
        connection.index = self.test_index
        catalog_store = Store(connection)
        catalog_store.list(item for item in file_list)
        time.sleep(1)

        file = open(self.test_path, 'a')
        file.write("Add one more line")
        file.close()

        self.assertEqual(sync_catalog_with_disk.main(['--index', self.test_index]), (1, 0, 6))

        time.sleep(1)
        os.remove(self.test_path)
        self.assertEqual(sync_catalog_with_disk.main(['--index', self.test_index]), (0, 1, 6))

    def test_clear_data(self):
        connection = Connection()
        connection.index = self.test_index
        delete = Delete(connection)
        reader = Retrieve(connection)

        delete.id_list([e for e in reader.all_ids()])
