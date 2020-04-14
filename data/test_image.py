from unittest import TestCase
from data.image import Image, InvalidImageError
from data.factory import Factory


class TestImage(TestCase):
    def test_name_invalid(self):
        image = Image()
        try:
            image.name = "myname.ext"
            self.fail("Should have raised exception")
        except InvalidImageError as e:
            self.assertTrue(type(e) is InvalidImageError)

    def test_jpeg_image(self):
        image = Image()
        image.name = "image.jpeg"
        self.assertEqual(image.type, "jpeg")
        self.assertEqual(image.kind, 0)
        self.assertEqual(image.name, "image.jpeg")

    def test_uppercase_image(self):
        image = Image()
        image.name = "MyPic.PNG"
        self.assertEqual(image.type, "png")
        self.assertEqual(image.kind, 0)
        self.assertEqual(image.name, "MyPic.PNG")

    def test_diff(self):
        image = Image()
        image.full_path = "/this/is/my/image.png"
        image.date = 1000000
        image.size = 10
        image.checksum = "ABCDEFGH"

        self.assertFalse(image.diff(image))

        image2 = Image()
        image2.full_path = image.full_path
        image2.date = 2000000
        image2.size = image.size
        image2.checksum = image.checksum

        self.assertEqual(image.diff(image2), {"created": image2.date})

    def test_same_file(self):
        image1 = Factory.from_path("../testfiles/spiderman.jpg")
        image2 = Factory.from_path("../testfiles/spidey.jpeg")
        self.assertNotIn("checksum", image1.diff(image2).keys())
        self.assertNotIn("size", image1.diff(image2).keys())
        self.assertIn("name", image1.diff(image2).keys())
