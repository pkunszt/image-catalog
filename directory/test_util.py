from unittest import TestCase


class TestDirectoryUtil(TestCase):

    def test_invalid_directory(self):
        from directory.util import Util
        util = Util()

        self.assertRaises(NotADirectoryError, util.check_that_this_is_a_directory, "./test_read.py")
