from unittest import TestCase
from data.image import Image, InvalidImageError


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
