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
        test_list = ImageList()

        file_list = test_list.scan_directory("./testfiles")
        names = []
        for item in file_list:
            names.append(item["name"])
        self.assertTrue("spiderman.jpg" in names)
        self.assertTrue("thor.jpeg" in names)
