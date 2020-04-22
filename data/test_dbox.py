import datetime
from unittest import TestCase
import os
from .dbox import DBox
from .factory import Factory, FactoryError
from constants import TestConstants
from data.directory import Folder


class TestDBox(TestCase):
    def test_list_dir(self):
        d = DBox(True)
        sorted_list = sorted([
            file
            for file in d.list_dir(os.path.join("/", TestConstants.testdir))
            if not file.endswith(".md")
        ])

        for i in range(0, len(sorted_list)):
            self.assertEqual(sorted_list[i], os.path.join("/", TestConstants.testdir, TestConstants.files[i]))

    def test_entries(self):
        d = DBox(True)
        st = []
        invalid_suffix = set()
        for path in d.list_dir(os.path.join("/", TestConstants.testdir)):
            try:
                st.append(Factory.from_dropbox(path))
            except FactoryError:
                invalid_suffix.add(os.path.splitext(path)[1])

        self.assertIn('.md', invalid_suffix)
        sorted_list = sorted(st, key=lambda x: x.name)

        for i in range(0, len(sorted_list)):
            self.assertEqual(TestConstants.files[i], sorted_list[i].name)
            self.assertEqual(TestConstants.sizes[i], sorted_list[i].size)
            self.assertEqual(TestConstants.types[i], sorted_list[i].type)
            self.assertEqual(TestConstants.kinds[i], sorted_list[i].kind)
            self.assertTrue(sorted_list[i].dropbox_path)

        for i in (0, 1):
            self.assertEqual(TestConstants.duration[i], sorted_list[i].duration)

        test_directory = Folder()
        mypath = os.path.abspath(os.getcwd())
        test_directory.read(os.path.join(mypath, TestConstants.testdir))
        sorted_dir = sorted(test_directory.file_list, key=lambda entry: entry.name)
        self.assertIn('.md', test_directory.invalid_types)

        for i in (0, 1):
            self.assertEqual(sorted_dir[i].duration, sorted_list[i].duration)

        for dbox_item, file_item in zip(sorted_list, sorted_dir):
            self.assertEqual(dbox_item.type, file_item.type)
            self.assertEqual(dbox_item.name, file_item.name)
            self.assertEqual(dbox_item.checksum, file_item.checksum)
            self.assertEqual(dbox_item.size, file_item.size)
            self.assertEqual(dbox_item.kind, file_item.kind)
            if hasattr(dbox_item, "captured") and hasattr(file_item, "captured"):
                self.assertEqual(dbox_item.captured, file_item.captured)

    def test_put_file(self):
        d = DBox(True)
        d.put_file(os.path.join(".", TestConstants.testdir, TestConstants.files[4]), TestConstants.sizes[4],
                   os.path.join("/", TestConstants.testdir, "testsubdir"), TestConstants.files[4],
                   datetime.datetime.fromtimestamp(987974751))

    def test_put_large_file(self):
        d = DBox(True)
        filename = os.path.join("/Users/pkunszt", "Downloads", "test.m4v")
        st = os.stat(filename)
        d.put_file(filename, st.st_size,
                   os.path.join("/", TestConstants.testdir, "testsubdir"), "test.m4v",
                   datetime.datetime.fromtimestamp(st.st_mtime))
