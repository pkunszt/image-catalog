from unittest import TestCase
from data.factory import Factory


class TestFactory(TestCase):
    def test_checksum(self):
        a = Factory.checksum("../testfiles/milky-way-nasa.jpg")
        self.assertEqual(a, "485291fa0ee50c016982abbfa943957bcd231aae0492ccbaa22c58e3997b35e0")
