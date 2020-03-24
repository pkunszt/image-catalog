import time
from unittest import TestCase
from images_in_directory import ImagesInDirectory
from typing import List
from elastic_storage import ElasticStorage
import warnings


class TestElasticStorage(TestCase):
    sorted_list: List
    testIndex = 'test_unit_elastic_storage'

    def setUp(self) -> None:
        time.sleep(1)
        test_directory = ImagesInDirectory()
        file_list = test_directory.scan("./testfiles")
        self.sorted_list = sorted(file_list, key=lambda i: i['name'])
        elastic_storage = ElasticStorage()
        id_list = elastic_storage.get_all_ids_in_index(self.testIndex)
        if len(id_list) > 0:
            elastic_storage.delete_id_list(self.testIndex, id_list)
        time.sleep(1)

    def test_store_image_list(self):
        elastic_storage = ElasticStorage()
        self.assertEqual(elastic_storage.store_image_list(self.sorted_list, self.testIndex), 4)
        # When trying again, none will be stored - they are already there
        time.sleep(1)
        self.assertEqual(elastic_storage.store_image_list(self.sorted_list, self.testIndex), 0)

    def test_store_video_list(self):
        elastic_storage = ElasticStorage()
        self.assertEqual(elastic_storage.store_video_list(self.sorted_list, self.testIndex), 1)
        # When trying again, none will be stored - they are already there
        time.sleep(1)
        self.assertEqual(elastic_storage.store_video_list(self.sorted_list, self.testIndex), 0)

    def test_delete_by_id_list(self):
        elastic_storage = ElasticStorage()
        id_list = elastic_storage.get_all_ids_in_index(self.testIndex)
        should = len(id_list)
        count = 0
        if should > 0:
            count = elastic_storage.delete_id_list(self.testIndex, id_list)
        self.assertEqual(count, should)

    def test_clear_exact_duplicates(self):
        elastic_storage = ElasticStorage(allow_duplicates=True)
        self.assertEqual(elastic_storage.store_image_list(self.sorted_list, self.testIndex), 4)
        self.assertEqual(elastic_storage.store_image_list(self.sorted_list, self.testIndex), 4)
        self.assertEqual(elastic_storage.store_video_list(self.sorted_list, self.testIndex), 1)

        time.sleep(1)
        count = elastic_storage.clear_exact_duplicates(self.testIndex, dry_run=False)
        self.assertEqual(count, 4)

    def test_build_duplicate_list_from_checksum(self):
        elastic_storage = ElasticStorage()
        elastic_storage.build_duplicate_list_from_checksum(self.testIndex)
        pass
