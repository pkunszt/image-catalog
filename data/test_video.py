from unittest import TestCase
from data.video import Video, InvalidVideoError
from constants import Constants


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
        self.assertEqual(video.kind, Constants.VIDEO_KIND)
        self.assertEqual(video.name, "video.AVI")
