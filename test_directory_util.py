from unittest import TestCase


class TestDirectoryUtil(TestCase):

    def test_get_file_type(self):
        from directory_util import DirectoryUtil
        file_type = DirectoryUtil.get_file_type("blah.jpg")
        self.assertEqual(file_type, "jpg")

        file_type = DirectoryUtil.get_file_type("blah.mov")
        self.assertEqual(file_type, "mov")

        file_type = DirectoryUtil.get_file_type("blah")
        self.assertEqual(file_type, "")

    def test_get_kind(self):
        from directory_util import DirectoryUtil
        util = DirectoryUtil()

        self.assertEqual(util.get_kind("jpeg"), 0)
        self.assertEqual(util.get_kind("MOV"), 1)
        self.assertEqual(util.get_kind("txt"), -1)
        self.assertEqual(util.get_kind("avi"), 1)

    def test_get_path_only(self):
        from directory_util import DirectoryUtil
        util = DirectoryUtil()

        self.assertEqual(util.get_path_only("one/two/three.four"), "one/two")
        self.assertEqual(util.get_path_only("./file.txt"), ".")
        self.assertEqual(util.get_path_only("file.txt"), "")
