from unittest import TestCase
from data.video import Video, InvalidVideoError


class TestVideo(TestCase):
    def test_name_invalid(self):
        video = Video()
        try:
            video.name = "myname.ext"
            self.fail("Should have raised exception")
        except InvalidVideoError as e:
            self.assertTrue(type(e) is InvalidVideoError)

    def test_avi_video(self):
        video = Video()
        video.name = "video.AVI"
        self.assertEqual(video.type, "avi")
        self.assertEqual(video.kind, 1)
        self.assertEqual(video.name, "video.AVI")
