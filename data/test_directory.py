from unittest import TestCase
from constants import Constants


class TestFolder(TestCase):

    def test_read(self):
        from data.directory import Folder
        files = ["P1030250.MOV", "boarding.mov", "cartoon.png", "food.heic",
                 "milky-way-nasa.jpg", "spiderman.jpg", "spidey.jpeg", "thor.jpeg", "ztest.psd"]
        sizes = [3691944, 30830885, 876273, 1643711, 9711423, 28398, 28398, 5906, 5]
        types = ["mov", "mov", "png", "heic", "jpg", "jpg", "jpeg", "jpeg", "psd"]
        kinds = [Constants.VIDEO_KIND]*2 + [Constants.IMAGE_KIND]*6 + [Constants.OTHER_KIND]
        duration = [11, 21]

        test_directory = Folder()
        test_directory.read("../testfiles")
        sorted_list = sorted(test_directory.file_list, key=lambda entry: entry.name)
        self.assertIn('.md', test_directory.invalid_types)

        for i in range(0, len(sorted_list)):
            self.assertEqual(files[i], sorted_list[i].name)
            self.assertEqual(sizes[i], sorted_list[i].size)
            self.assertEqual(types[i], sorted_list[i].type)
            self.assertEqual(kinds[i], sorted_list[i].kind)

        for i in (0, 1):
            self.assertEqual(duration[i], sorted_list[i].duration)

        self.assertEqual("4032x3024", sorted_list[3].dimensions)
        self.assertEqual("2020-02-08 19-10-04", sorted_list[3].captured_str)
        self.assertEqual('47.50632,8.69123', sorted_list[3].location)

    def test_scan_invalid_directory_to_read(self):
        from data.directory import Folder
        test_directory = Folder()

        self.assertRaises(NotADirectoryError, test_directory.read, "blah")
        self.assertRaises(NotADirectoryError, test_directory.read, "./test_directory.py")
