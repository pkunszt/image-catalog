import hashlib

from elasticsearch import Elasticsearch
from typing import List, Dict


class ElasticStorageError(EnvironmentError):
    def __init__(self, message: str):
        super(message)


class ElasticStorage:
    """Class to store json data in elastic"""
    __elastic: Elasticsearch
    __duplicate_dict: dict

    image_index: str
    video_index: str

    item_type_to_index_map: Dict[int, str]

    def __init__(self, host: str = 'localhost', port: int = 9200):
        self.__duplicate_dict = {}
        self.__elastic = Elasticsearch([{'host': host, 'port': port}])
        self.image_index = 'images'
        self.video_index = 'videos'
        self.item_type_to_index_map = {0: self.image_index, 1: self.video_index}

    def store_image_list(self, images: List[dict], index: str = None) -> int:
        kind_map = self.item_type_to_index_map.copy()
        del kind_map[1]
        if index is not None:
            kind_map[0] = index
        return self.__store_list(images, kind_map)

    def store_video_list(self, videos: List[dict], index: str = None) -> int:
        kind_map = self.item_type_to_index_map.copy()
        del kind_map[0]
        if index is not None:
            kind_map[1] = index
        return self.__store_list(videos, kind_map)

    def store_list(self, items: List[dict], kind_map: Dict[int, str] = None) -> int:
        if kind_map is None:
            kind_map = self.item_type_to_index_map
        return self.__store_list(items, kind_map)

    def __store_list(self, items: List[dict], kind_map: Dict[int, str]) -> int:
        count = 0
        for item in items:
            if item['kind'] in kind_map.keys():
                self.__elastic.index(index=kind_map[item['kind']], body=item)
                count = count + 1
        return count

    def build_duplicate_list_from_full_content(self, index: str) -> None:
        data = self.__elastic.search(index=index, scroll='1m', body={"query": {"match_all": {}}})
        self.build_list_of_ids(data, True)

    def get_all_ids_in_index(self, index: str) -> List:
        data = self.__elastic.search(index=index, scroll='1m', body={"query": {"match_all": {}}, "stored_fields": []})
        id_list = []
        while True:
            sid = data['_scroll_id']
            scroll_size = len(data['hits']['hits'])
            for hit in data['hits']['hits']:
                id_list.append(hit['_id'])
            if scroll_size == 0:
                break
            data = self.__elastic.scroll(scroll_id=sid, scroll='2m')

        return id_list

    def clear_exact_duplicates(self, index: str, dry_run: bool = True) -> int:
        count = 0
        self.build_duplicate_list_from_full_content(index)
        for hash_val, array_of_ids in self.__duplicate_dict.items():
            if len(array_of_ids) > 1:
                if not dry_run:
                    self.delete_id_list(index, array_of_ids[1:])
                count = count + len(array_of_ids) - 1

        return count

    def delete_id_list(self, index: str, array_of_ids: List[str]) -> int:
        result = self.__elastic.delete_by_query(index=index, body={"query": {"ids": {"values": array_of_ids}}})
        if len(result['failures']) > 0:
            raise ElasticStorageError("Failed Delete " + result['failures'])
        if result['deleted'] != len(array_of_ids):
            raise ElasticStorageError("Failed Delete: expected "+str(len(array_of_ids))+" got "+result('deleted'))
        return result['deleted']

    def delete_id(self, index, _id) -> None:
        id_array = [_id]
        self.delete_id_list(index, id_array)

    def build_list_of_ids(self, data, full_content: bool = False) -> None:
        self.__duplicate_dict.clear()
        sid = data['_scroll_id']
        scroll_size = len(data['hits']['hits'])
        self.fill_dictionary(data['hits']['hits'], full_content)
        while scroll_size > 0:
            data = self.__elastic.scroll(scroll_id=sid, scroll='2m')
            self.fill_dictionary(data['hits']['hits'], full_content)
            sid = data['_scroll_id']
            scroll_size = len(data['hits']['hits'])

    def fill_dictionary(self, result: dict, full_content: bool) -> None:
        for item in result:
            if not full_content:
                hash_val = item['_source']['checksum']
            else:
                value = ''
                for key in item['_source'].keys():
                    value = value + str(item['_source'][key])
                hash_val = hashlib.md5(value.encode('utf-8')).digest()

            self.__duplicate_dict.setdefault(hash_val, []).append(item['_id'])

    def build_duplicate_list_from_checksum(self, index: str) -> None:
        data = self.__elastic.search(index=index, scroll='1m', body={"query": {"match_all": {}}})
        self.build_list_of_ids(data, False)

