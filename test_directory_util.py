from unittest import TestCase


class TestDirectoryUtil(TestCase):

    def test_get_file_type_from_valid_file(self):
        from directory_util import DirectoryUtil
        file_type = DirectoryUtil.get_file_type("blah.jpg")
        self.assertEqual(file_type, "jpg")
        file_type = DirectoryUtil.get_file_type("whatever.blah.mov")
        self.assertEqual(file_type, "mov")

    def test_get_file_type_from_file_without_type(self):
        from directory_util import DirectoryUtil
        file_type = DirectoryUtil.get_file_type("blah")
        self.assertEqual(file_type, "")

    def test_get_kind_with_valid_image_and_video_types(self):
        from directory_util import DirectoryUtil
        util = DirectoryUtil()

        self.assertEqual(util.get_kind("jpeg"), 0)
        self.assertEqual(util.get_kind("MOV"), 1)
        self.assertEqual(util.get_kind("avi"), 1)
        self.assertEqual(util.get_kind("GIF"), 0)

    def test_get_kind_with_invalid_types(self):
        from directory_util import DirectoryUtil
        util = DirectoryUtil()

        self.assertEqual(util.get_kind("txt"), -1)
        self.assertEqual(util.get_kind("XLS"), -1)

    def test_get_path_only_with_full_path(self):
        from directory_util import DirectoryUtil
        util = DirectoryUtil()
        self.assertEqual(util.get_path_only("/one/two/three.four"), "/one/two")
        self.assertEqual(util.get_path_only("/every/thing/has/something/at/the/end/file.name"),
                         "/every/thing/has/something/at/the/end")

    def test_get_path_only_with_relative_path(self):
        from directory_util import DirectoryUtil
        util = DirectoryUtil()
        self.assertEqual(util.get_path_only("./file.txt"), ".")
        self.assertEqual(util.get_path_only("./some/file/dir/file.txt"), "./some/file/dir")

    def test_get_path_only_with_no_path(self):
        from directory_util import DirectoryUtil
        util = DirectoryUtil()
        self.assertEqual(util.get_path_only("file.txt"), "")

    def test_invalid_directory(self):
        from directory_util import DirectoryUtil
        util = DirectoryUtil()

        self.assertRaises(NotADirectoryError, util.check_that_this_is_a_directory, "./test_images_in_directory.py")
