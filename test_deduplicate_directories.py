import unittest
import os
import shutil
import time
import deduplicate_directories
from data import Folder
from elastic import Store, Connection, Retrieve


class TestDeduplicateDirectories(unittest.TestCase):

    def test_deduplicate(self):
        test_dir = "./testfiles"
        test_name = "spidey.jpeg"
        test_source = "spiderman.jpg"
        test_path = os.path.join(test_dir, test_name)
        test_source_path = os.path.join(test_dir, test_source)
        test_index = 'test_dedupdir'

        if not os.path.exists(test_path):
            shutil.copy2(test_source_path, test_path)

        test_directory = Folder()
        test_directory.read(test_dir)
        file_list = test_directory.file_list
        connection = Connection()
        connection.index = test_index
        catalog_store = Store(connection)
        catalog_store.list(item for item in file_list)
        time.sleep(1)

        deduplicate_directories.main(['--index', test_index])
        self.assertFalse(os.path.exists(test_path))

        time.sleep(1)
        retrieve = Retrieve(connection)
        entry_list = [
            entry.name
            for entry in retrieve.all_entries()
        ]
        self.assertNotIn(test_name, entry_list)
        shutil.copy2(test_source_path, test_path)


if __name__ == '__main__':
    unittest.main()
