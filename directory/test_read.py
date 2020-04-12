from unittest import TestCase


class TestReader(TestCase):

    def test_scan(self):
        from directory.read import Reader
        files = ["P1030250.MOV", "cartoon.png", "spiderman.jpg", "spidey.jpeg", "thor.jpeg"]
        sizes = [3691944, 876273, 28398, 28398, 5906]
        types = ["mov", "png", "jpg", "jpeg", "jpeg"]
        kinds = [1, 0, 0, 0, 0]
        test_directory = Reader("../testfiles")
        sorted_list = sorted(test_directory.file_list, key=lambda entry: entry.name)

        for i in range(0, len(sorted_list)):
            self.assertEqual(files[i], sorted_list[i].name)
            self.assertEqual(sizes[i], sorted_list[i].size)
            self.assertEqual(types[i], sorted_list[i].type)
            self.assertEqual(kinds[i], sorted_list[i].kind)

    def test_scan_invalid_directory_to_scan(self):
        from directory.read import Reader
        test_directory = Reader()

        self.assertRaises(NotADirectoryError, test_directory.read, "blah")
        self.assertRaises(NotADirectoryError, test_directory.read, "./test_read.py")
