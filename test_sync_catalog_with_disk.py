import os
import time
from unittest import TestCase
import sync_catalog_with_disk
from directory import Reader
from elastic import Store, Connection


class TestSyncCatalogWithDisk(TestCase):
    def test_sync(self):
        testfile = "testfile.mov"
        testdir = "./testfiles"
        testindex = 'test_sync'
        testpath = os.path.join(testdir, testfile)

        if not os.path.exists(testpath):
            file = open(testpath, 'w')
            file.writelines(["This is a testfile", "just some text, really"])
            file.close()

        test_directory = Reader()
        test_directory.read(testdir)
        file_list = test_directory.file_list
        connection = Connection()
        connection.index = testindex
        catalog_store = Store(connection)
        catalog_store.list(item for item in file_list)
        time.sleep(1)

        file = open(testpath, 'a')
        file.write("Add one more line")
        file.close()

        self.assertEqual(sync_catalog_with_disk.main(['--index', 'test_sync']), (1, 0, 6))

        time.sleep(1)
        os.remove(testpath)
        self.assertEqual(sync_catalog_with_disk.main(['--index', 'test_sync']), (0, 1, 6))
