from unittest import TestCase


class TestImageList(TestCase):
    def test_get_type(self):
        from image_list import ImageList
        file_type = ImageList.get_file_type("blah.jpg")
        self.assertEqual(file_type, "jpg")

        file_type = ImageList.get_file_type("blah.mov")
        self.assertEqual(file_type, "mov")

        file_type = ImageList.get_file_type("blah")
        self.assertEqual(file_type, "")

    def test_get_kind(self):
        from image_list import ImageList
        test_list = ImageList()

        self.assertEqual(test_list.get_kind("jpg"), 0)
        self.assertEqual(test_list.get_kind("mov"), 1)
        self.assertEqual(test_list.get_kind("txt"), -1)
        self.assertEqual(test_list.get_kind("avi"), 1)
        self.assertEqual(test_list.get_kind("txt"), -1)

        self.assertEqual(test_list.get_invalid_types_found(), {"txt"})

    def test_scan(self):
        from image_list import ImageList
        files = ["cartoon.png", "spiderman.jpg", "spidey.jpeg", "thor.jpeg"]
        sizes = [876273, 28398, 28398, 5906]
        types = ["png", "jpg", "jpeg", "jpeg"]
        kinds = [0, 0, 0, 0]
        test_list = ImageList()

        file_list = test_list.scan_directory("./testfiles")
        sorted_list = sorted(file_list, key=lambda i: i['name'])

        for i in range(0, len(file_list)):
            self.assertEqual(files[i], sorted_list[i]['name'])
            self.assertEqual(sizes[i], sorted_list[i]['size'])
            self.assertEqual(types[i], sorted_list[i]['type'])
            self.assertEqual(kinds[i], sorted_list[i]['kind'])

    def test_scan_invalid_input(self):
        from image_list import ImageList
        test_list = ImageList()

        self.assertRaises(FileNotFoundError, test_list.scan_directory, "blah")
        self.assertRaises(NotADirectoryError, test_list.scan_directory, "./test_image_list.py")

    def test_get_path_only(self):
        from image_list import ImageList
        test_list = ImageList()

        self.assertEqual(test_list.get_path_only("one/two/three.four"), "one/two")
        self.assertEqual(test_list.get_path_only("./file.txt"), ".")
        self.assertEqual(test_list.get_path_only("file.txt"), "")
