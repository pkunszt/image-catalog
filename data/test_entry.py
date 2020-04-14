from unittest import TestCase
from data.entry import Entry, EntryException


class TestEntry(TestCase):
    def test_to_dict(self):
        e = Entry()
        self.assertRaises(EntryException, e.to_dict)

    def test_name_simple_filename(self):
        entry = Entry()
        entry.name = "myfile.ext"
        self.assertEqual(entry.name, "myfile.ext")
        self.assertEqual(entry.type, "ext")

    def test_name_invalid_path(self):
        entry = Entry()
        try:
            entry.name = "somepath/myname.ext"
            self.fail("Should have raised exception")
        except EntryException as e:
            self.assertEqual(e.args[0].find("File name given must just"), 0)

    def test_set_full_path(self):
        entry = Entry()
        entry.full_path = "/this/is/somepath/myname.ext"
        self.assertEqual(entry.name, "myname.ext")
        self.assertEqual(entry.path, "/this/is/somepath")
        self.assertEqual(entry.type, "ext")

    def test_set_full_path_relative(self):
        entry = Entry()
        entry.full_path = "../this/is/somepath/myname.ext"
        self.assertEqual(entry.name, "myname.ext")
        self.assertEqual(entry.path, "../this/is/somepath")
        self.assertEqual(entry.type, "ext")

    def test_set_date(self):
        entry = Entry()
        entry.modified = 0
        self.assertEqual(entry.modified_str, "1970-01-01")
