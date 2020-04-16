from typing import Generator
from elasticsearch import Elasticsearch, NotFoundError
from elasticsearch_dsl import Search
from elastic.connection import Connection


class StorageError(ValueError):
    def __init__(self, message: str):
        super().__init__(message)


class Store:

    __elastic: Elasticsearch
    __allow_duplicates: bool
    __index: str

    def __init__(self, connection: Connection, allow_duplicates: bool = False):
        self.__elastic = connection.get()
        self.__index = connection.index
        self.__allow_duplicates = allow_duplicates

    @property
    def allow_duplicates(self) -> bool:
        return self.__allow_duplicates

    @allow_duplicates.setter
    def allow_duplicates(self, flag: bool):
        self.__allow_duplicates = flag

    @property
    def index(self) -> str:
        return self.__index

    @property
    def elastic(self):
        return self.__elastic

    def list(self, entries: Generator) -> int:
        count = 0
        for e in entries:
            if e.kind not in (0, 1):
                raise StorageError(f"Invalid kind {str(e.kind)} in list for {e.name}")
            hits = 0
            if not self.allow_duplicates:
                s = Search(using=self.elastic, index=self.index).filter('term', hash=e.hash)
                try:
                    result = s.execute()
                    hits = len(result.hits)
                except NotFoundError:
                    print(f"The index {self.index} does not exist yet, creating it")
                    self.create_index()
            if self.allow_duplicates or hits == 0:
                self.elastic.index(index=self.index, body=e.to_dict())
                count = count + 1
        return count

    def update(self, change, _id: str):
        self.elastic.update(index=self.index, id=_id, body={'doc': change})

    def create_index(self):
        self.elastic.create(index=self.index, body={
            "mappings": {
                "properties": {
                    "name": {"type": "text"},
                    "path": {"type": "text"},
                    "size": {"type": "integer"},
                    "duration": {"type": "integer"},
                    "captured": {"type": "date"},
                    "modified": {"type": "date"},
                    "kind": {"type": "keyword"},
                    "type": {"type": "keyword"},
                    "hash": {"type": "keyword"},
                    "checksum": {"type": "keyword"},
                    "location": {"type": "geo_point"}
                }
            }
        })
