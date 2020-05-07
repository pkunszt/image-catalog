from unittest import TestCase
import os
from catalog import TestConstants, Constants
from data import Image
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

    def test_set_name(self):
        image = Image()
        image.full_path = "/some/path/name is a string.jpg"
        image.size = 1234
        image.modified = TestConstants.modified_test
        self.assertEqual(image.modified_time_str, TestConstants.modified_test_str)

        # Test that an image without captured date retains its name if we want to change only by captured date
        doc = image.name
        Folder.set_name(image, name_from_captured_date=True,
                        name_from_modified_date=False,
                        keep_manual_names=False)
        self.assertEqual(doc, image.name)

        # An image without captured date but with modified date changes name if we want to change by mod date
        Folder.set_name(image, name_from_captured_date=False,
                        name_from_modified_date=True,
                        keep_manual_names=False)
        self.assertEqual(image.name, TestConstants.modified_test_str + '@' + doc)

        image.name = doc
        # If the image has a meaningful name, modified date is not prepended if we want to keep manual names
        Folder.set_name(image, name_from_captured_date=False,
                        name_from_modified_date=True,
                        keep_manual_names=True)
        self.assertEqual(doc, image.name)

        # If image has no meaningful name, then modified time IS prepended also if we want to keep manual names
        image.name = doc = "IMG324342.jpg"
        Folder.set_name(image, name_from_captured_date=False,
                        name_from_modified_date=True,
                        keep_manual_names=True)
        self.assertEqual(image.name, TestConstants.modified_test_str + '@' + doc)

        image.name = doc = "name is a string.jpg"
        # add now captured date
        image.captured = TestConstants.captured_test
        self.assertEqual(image.captured_str, TestConstants.captured_test_str)

        # if we have a captured date and want to change by it, the whole name is changed
        Folder.set_name(image, name_from_captured_date=True,
                        name_from_modified_date=False,
                        keep_manual_names=False)
        self.assertEqual(image.name, TestConstants.captured_test_str + '.' + image.type)

        # if we want to change by modified name, but we do have captured date, also then captured date is set
        image.name = doc
        Folder.set_name(image, name_from_captured_date=False,
                        name_from_modified_date=True,
                        keep_manual_names=False)
        self.assertEqual(image.name, TestConstants.captured_test_str + '.' + image.type)

        # if we have some meaningful name, and want to keep it, the captured date is appended to it
        name, ext = os.path.splitext(doc)
        image.name = doc
        Folder.set_name(image, name_from_captured_date=False,
                        name_from_modified_date=False,
                        keep_manual_names=True)
        self.assertEqual(image.name, name + ' ' + TestConstants.captured_test_str + ext)

        # if the name is not meaningful, replace it with the captured date even if not asked for
        image.name = doc = "IMG324342.jpg"
        name, ext = os.path.splitext(doc)
        Folder.set_name(image, name_from_captured_date=False,
                        name_from_modified_date=False,
                        keep_manual_names=True)
        self.assertEqual(image.name, TestConstants.captured_test_str + ext)

    def test_update_filmchen_and_locations(self):
        test_directory = Folder()
        test_directory.read(os.path.join("..", TestConstants.testdir))

        test_directory.update_filmchen_and_locations()
        for item in test_directory.files:
            if item.kind == Constants.VIDEO_KIND:
                self.assertEqual(os.path.basename(item.path), 'filmchen')
            if item.type == 'heic':
                self.assertEqual(item.name.split(' ')[-1], "Winterthur.heic")
