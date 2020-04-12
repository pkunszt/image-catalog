from unittest import TestCase
from elastic.index import Index


class TestIndex(TestCase):
    def test_image(self):
        i = Index()
        self.assertEqual(i.video, 'videos')
        self.assertEqual(i.image, 'images')

        self.assertEqual(i.map[0], 'images')

    def test_video(self):
        i = Index()
        i.video = 'bla'
        self.assertEqual(i.map[1], 'bla')

        i.map[0] = 'gugus'
        self.assertEqual(i.map[0], 'gugus')
        self.assertEqual(i.image, 'images')

    def test_invalid_map_index(self):
        i = Index()
        try:
            a = i.from_kind(-1)
            self.fail("This should fail")
        except KeyError:
            pass

    def test_remove_map_index(self):
        i = Index()
        self.assertEqual(i.map.pop(0), 'images')
        self.assertRaises(KeyError, i.from_kind, 0)
        i.image = 'bla'
        self.assertEqual(i.from_kind(0), 'bla')

    def test_remove_and_restore_map(self):
        i = Index()
        self.assertEqual(i.map.pop(0), 'images')
        self.assertRaises(KeyError, i.from_kind, 0)
        i.image = i.image
        self.assertEqual(i.from_kind(0), 'images')
