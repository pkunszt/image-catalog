from elasticsearch import Elasticsearch, NotFoundError
from elasticsearch_dsl import Search, connections
from typing import List, Dict


class ElasticStorageError(EnvironmentError):
    def __init__(self, message: str):
        super(message)


class ElasticStorage:
    """Class to store json data in elastic"""
    __elastic: Elasticsearch
    __connection: connections.Connections
    __duplicate_dict: dict

    image_index: str
    video_index: str

    item_type_to_index_map: Dict[int, str]

    # The connection is a static class variable, reused every time
    __connection = connections.Connections()

    def __init__(self, host: str = 'localhost', port: int = 9200, allow_duplicates: bool = False):
        self.__duplicate_dict = {}
        self.__get_connection(host, port)
        self.image_index = 'images'
        self.video_index = 'videos'
        self.item_type_to_index_map = {0: self.image_index, 1: self.video_index}
        self.__allow_duplicates = allow_duplicates

    def __get_connection(self, host: str, port: int) -> None:
        """The connection is reused. On first try there will be no 'elastic' connection. Create it.
        Will create different connections for each host:port combination, by using that in the name."""

        connection_name = 'elastic'+'host'+str(port)
        try:
            self.__elastic = type(self).__connection.get_connection(connection_name)
        except KeyError:
            type(self).__connection.configure(**{connection_name: {'hosts': [host + ':' + str(port)]}})
            self.__elastic = type(self).__connection.get_connection(connection_name)

    def close_connection(self, host: str, port: int) -> None:
        """Force closing connection to elastic on given host and port. Only use if you know what you are doing"""
        connection_name = 'elastic'+'host'+str(port)
        try:
            type(self).__connection.get_connection(connection_name)
        except KeyError:
            return
        type(self).__connection.remove_connection(connection_name)
        print("closed connection to "+host+':'+str(port))

    def store_image_list(self, images: List[dict], index: str = None) -> int:
        """Store only images from the given list."""
        kind_map = self.item_type_to_index_map.copy()
        del kind_map[1]
        if index is not None:
            kind_map[0] = index
        return self.__store_list(images, kind_map)

    def store_video_list(self, videos: List[dict], index: str = None) -> int:
        """Store only videos from the given list."""
        kind_map = self.item_type_to_index_map.copy()
        del kind_map[0]
        if index is not None:
            kind_map[1] = index
        return self.__store_list(videos, kind_map)

    def store_list(self, items: List[dict], kind_map: Dict[int, str] = None) -> int:
        """Store both images and videos from the given list."""
        if kind_map is None:
            kind_map = self.item_type_to_index_map
        return self.__store_list(items, kind_map)

    def __store_list(self, items: List[dict], kind_map: Dict[int, str]) -> int:
        count = 0
        for item in items:
            if item['kind'] in kind_map.keys():
                hits = 0
                if not self.__allow_duplicates:
                    # Check whether the hash is already in the catalog.
                    s = Search(using=self.__elastic, index=kind_map[item['kind']]).filter('term', hash=item['hash'])
                    try:
                        result = s.execute()
                        hits = len(result.hits)
                    except NotFoundError: # when running for the very first time, the index is not there yet
                        pass
                # Only store it if it is not there already (no hit found on hash).
                if self.__allow_duplicates or hits == 0:
                    self.__elastic.index(index=kind_map[item['kind']], body=item)
                    count = count + 1
        return count

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

    def delete_id(self, index: str, _id: str) -> None:
        id_array = [_id]
        self.delete_id_list(index, id_array)

    def build_duplicate_list_from_full_content(self, index: str) -> None:
        s = Search(using=self.__elastic, index=index)
        for entry in s.scan():
            self.add_dictionary(entry, True)

    def add_dictionary(self, entry, full_content: bool):
        if not full_content:
            hash_val = entry.checksum
        else:
            hash_val = entry.hash
        self.__duplicate_dict.setdefault(hash_val, []).append(entry.meta.id)

    def build_duplicate_list_from_checksum(self, index: str) -> None:
        s = Search(using=self.__elastic, index=index)
        for entry in s.scan():
            self.add_dictionary(entry, False)

        for hash_val, array_of_ids in self.__duplicate_dict.items():
            if len(array_of_ids) > 1:
                print(array_of_ids)

