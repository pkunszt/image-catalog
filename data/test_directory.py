from unittest import TestCase
import os
from constants import TestConstants
from data.directory import Folder


class TestFolder(TestCase):

    def test_read(self):

        test_directory = Folder()
        test_directory.read(os.path.join("..", TestConstants.testdir))
        sorted_list = sorted(test_directory.file_list, key=lambda entry: entry.name)
        self.assertIn('.md', test_directory.invalid_types)

        for i in range(0, len(sorted_list)):
            self.assertEqual(TestConstants.files[i], sorted_list[i].name)
            self.assertEqual(TestConstants.sizes[i], sorted_list[i].size)
            self.assertEqual(TestConstants.types[i], sorted_list[i].type)
            self.assertEqual(TestConstants.kinds[i], sorted_list[i].kind)

        for i in (0, 1):
            self.assertEqual(TestConstants.duration[i], sorted_list[i].duration)

        self.assertEqual("4032x3024", sorted_list[3].dimensions)
        self.assertEqual("2020-02-08 19-10-04", sorted_list[3].captured_str)
        self.assertEqual('47.50632,8.69123', sorted_list[3].location)

    def test_scan_invalid_directory_to_read(self):
        test_directory = Folder()

        self.assertRaises(NotADirectoryError, test_directory.read, "blah")
        self.assertRaises(NotADirectoryError, test_directory.read, "./test_directory.py")
