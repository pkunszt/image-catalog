from unittest import TestCase

from elastic import Connection, Retrieve


class TestRetrieve(TestCase):
    def test_all_entries(self):
        c = Connection()
        r = Retrieve(c)
        for item in r.all_entries("2002/01_January"):
            print(item.name)
