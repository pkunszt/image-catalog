import time
from unittest import TestCase
from images_in_directory import ImagesInDirectory
from typing import List
from elastic_storage import ElasticStorage


class TestElasticStorage(TestCase):
    sorted_list: List
    testIndex = 'test_unit_elastic_storage'

    def setUp(self) -> None:
        test_directory = ImagesInDirectory()
        self.elastic_storage = ElasticStorage()
        file_list = test_directory.scan("./testfiles")
        self.sorted_list = sorted(file_list, key=lambda i: i['name'])

    def test_store_image_list(self):
        self.assertEqual(self.elastic_storage.store_image_list(self.sorted_list, self.testIndex), 4)

    def test_store_video_list(self):
        self.assertEqual(self.elastic_storage.store_video_list(self.sorted_list, self.testIndex), 1)

    def test_delete_by_id_list(self):
        id_list = self.elastic_storage.get_all_ids_in_index(self.testIndex)
        count = self.elastic_storage.delete_id_list(self.testIndex, id_list)
        self.assertEqual(count, 5)

    def test_clear_exact_duplicates(self):
        self.assertEqual(self.elastic_storage.store_image_list(self.sorted_list, self.testIndex), 4)
        self.assertEqual(self.elastic_storage.store_image_list(self.sorted_list, self.testIndex), 4)
        self.assertEqual(self.elastic_storage.store_video_list(self.sorted_list, self.testIndex), 1)

        time.sleep(1)
        count = self.elastic_storage.clear_exact_duplicates(self.testIndex, dry_run=False)
        self.assertEqual(count, 4)
