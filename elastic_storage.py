from elasticsearch import Elasticsearch, NotFoundError
from elasticsearch_dsl import Search, connections, A
from typing import List, Dict


class ElasticStorageError(EnvironmentError):
    def __init__(self, message: str):
        super().__init__(message)


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

    def store_image_list(self, images: List[dict]) -> int:
        """Store only images from the given list."""
        kind_map = self.item_type_to_index_map.copy()
        del kind_map[1]
        return self.__store_list(images, kind_map)

    def store_video_list(self, videos: List[dict]) -> int:
        """Store only videos from the given list."""
        kind_map = self.item_type_to_index_map.copy()
        del kind_map[0]
        return self.__store_list(videos, kind_map)

    def store_list(self, items: List[dict], kind_map: Dict[int, str] = None) -> int:
        """Store both images and videos from the given list."""
        if kind_map is None:
            kind_map = self.item_type_to_index_map
        return self.__store_list(items, kind_map)

    def __store_list(self, items: List[dict], kind_map: Dict[int, str]) -> int:
        count: int = 0
        for item in items:
            if item['kind'] in kind_map.keys():
                hits = 0
                if not self.__allow_duplicates:
                    # Check whether the hash is already in the catalog.
                    s = Search(using=self.__elastic, index=kind_map[item['kind']]).filter('term', hash=item['hash'])
                    try:
                        result = s.execute()
                        hits = len(result.hits)
                    except NotFoundError:  # when running for the very first time, the index is not there yet
                        pass
                # Only store it if it is not there already (no hit found on hash).
                if self.__allow_duplicates or hits == 0:
                    self.__elastic.index(index=kind_map[item['kind']], body=item)
                    count = count + 1
        return count

    def all_ids_in_index(self, index: str):
        data = self.__elastic.search(index=index, scroll='1m', body={"query": {"match_all": {}}, "stored_fields": []})
        while True:
            sid = data['_scroll_id']
            scroll_size = len(data['hits']['hits'])
            for hit in data['hits']['hits']:
                yield hit['_id']
            if scroll_size == 0:
                break
            data = self.__elastic.scroll(scroll_id=sid, scroll='2m')

    def clear_exact_duplicates_from_index(self, video: bool = False, dry_run: bool = True) -> int:
        count = 0
        index = self.set_index(video)
        self.build_duplicate_list_from_full_content(video)
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
            err_str = "Failed Delete: expected "+str(len(array_of_ids))+" got "+str(result['deleted'])
            raise ElasticStorageError(err_str)
        return result['deleted']

    def delete_id(self, index: str, _id: str) -> None:
        result = self.__elastic.delete(index=index, id=_id)
        if result['result'] != 'deleted':
            raise ElasticStorageError("Failed Delete " + result['result'])

    def get_image_by_id(self, i: str):
        return self.get_by_id(self.image_index, i)

    def get_video_by_id(self, i: str):
        return self.get_by_id(self.video_index, i)

    def get_by_id(self, index: str, i: str):
        result = self.__elastic.get(index=index, id=i, _source_includes=['path', 'name'])
        return result['_source']

    def set_index(self, video: bool = False) -> str:
        index = self.image_index
        if video:
            index = self.video_index
        return index

    def scan_index(self, video: bool = False, directory_filter: str = None):
        index = self.set_index(video)
        s = Search(using=self.__elastic, index=index)
        if directory_filter is not None:
            s = s.filter('match_phrase', path=directory_filter)
        for entry in s.scan():
            yield entry

    def build_duplicate_list_from_full_content(self, video: bool = False) -> None:
        for entry in self.scan_index(video=video):
            self.__duplicate_dict.setdefault(entry.hash, []).append(entry.meta.id)

    def build_duplicate_list_from_checksum(self, directory_filter: str = None,
                                           video: bool = False) -> None:
        for entry in self.scan_index(video=video, directory_filter=directory_filter):
            self.__duplicate_dict.setdefault(entry.checksum+entry.path, []).append(entry.meta.id)

    def clear_duplicate_list(self):
        self.__duplicate_dict = dict()

    def get_found_duplicate_ids(self) -> list:
        result = []
        for hash_val, array_of_ids in self.__duplicate_dict.items():
            if len(array_of_ids) > 1:
                result.append(array_of_ids)  # get last element of list

        return result

    def elastic_connection(self, host: str, port: int):
        self.__get_connection(host, port)
        return self.__elastic

    def all_paths(self, video: bool = False):
        index = self.set_index(video)

        #
        # Elastic will partition the aggregation result automatically into 20 parts in our case.
        # The size parameter just has to be large enough to hold a single partition, but
        # when called, it will just hold 1/20th of the total result set, so far less usually.
        #
        # The 'yield' construct makes this method into a generator, to be used as an iterator
        # in a loop, to retrieve each result individually. It will jump to the next partition
        # automatically when the current one was exhausted.
        #

        i = 0
        partitions = 20
        while i < partitions:
            s = Search(using=self.__elastic, index=index).extra(size=0)
            path_aggregation = A('terms', field='path.keyword', size=999999,
                                 include={"partition": i, "num_partitions": partitions})
            s.aggs.bucket('paths', path_aggregation)
            result = s.execute()
            for path in result.aggregations.paths.buckets:
                yield path.key
            i = i + 1

    def update(self, change, _id: str, video: bool = False):
        index = self.set_index(video)
        self.__elastic.update(index=index, id=_id, body={'doc': change})
