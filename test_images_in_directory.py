from unittest import TestCase


class TestImagesInDirectory(TestCase):

    def test_get_invalid_types_found(self):
        from images_in_directory import ImagesInDirectory
        from directory_util import DirectoryUtil
        util = DirectoryUtil()
        test_directory = ImagesInDirectory()

        # reference to private method for testing purposes.
        self.assertEqual(util.get_kind("jpg", test_directory._ImagesInDirectory__add_invalid_type), 0)
        self.assertEqual(util.get_kind("mov", test_directory._ImagesInDirectory__add_invalid_type), 1)
        self.assertEqual(util.get_kind("txt", test_directory._ImagesInDirectory__add_invalid_type), -1)
        self.assertEqual(util.get_kind("avi", test_directory._ImagesInDirectory__add_invalid_type), 1)
        self.assertEqual(util.get_kind("txt", test_directory._ImagesInDirectory__add_invalid_type), -1)

        self.assertEqual(test_directory.get_invalid_types_found(), {"txt"})

    def test_scan(self):
        from images_in_directory import ImagesInDirectory
        files = ["P1030250.MOV", "cartoon.png", "spiderman.jpg", "spidey.jpeg", "thor.jpeg"]
        sizes = [3691944, 876273, 28398, 28398, 5906]
        types = ["mov", "png", "jpg", "jpeg", "jpeg"]
        kinds = [1, 0, 0, 0, 0]
        test_directory = ImagesInDirectory()

        file_list = test_directory.scan("./testfiles")
        sorted_list = sorted(file_list, key=lambda i: i['name'])

        for i in range(0, len(file_list)):
            self.assertEqual(files[i], sorted_list[i]['name'])
            self.assertEqual(sizes[i], sorted_list[i]['size'])
            self.assertEqual(types[i], sorted_list[i]['type'])
            self.assertEqual(kinds[i], sorted_list[i]['kind'])

    def test_scan_invalid_directory_to_scan(self):
        from images_in_directory import ImagesInDirectory
        test_directory = ImagesInDirectory()

        self.assertRaises(FileNotFoundError, test_directory.scan, "blah")
        self.assertRaises(NotADirectoryError, test_directory.scan, "./test_images_in_directory.py")

