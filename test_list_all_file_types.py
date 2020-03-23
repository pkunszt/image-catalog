from unittest import TestCase


class TestListAllFileTypes(TestCase):
    def test_scan(self):
        from list_all_file_types import ListAllFileTypes
        test_directory_list = ListAllFileTypes("./testfiles")
        self.assertEqual(test_directory_list.get_list_of_found_types(), {"jpg", "png", "jpeg", "mov"})

    def test_scan_invalid_directory_to_scan(self):
        from list_all_file_types import ListAllFileTypes
        test_directory = ListAllFileTypes()

        self.assertRaises(FileNotFoundError, test_directory.scan, "blah")
        self.assertRaises(NotADirectoryError, test_directory.scan, "./test_images_in_directory.py")
