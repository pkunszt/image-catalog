from typing import Generator
from elasticsearch import Elasticsearch, NotFoundError
from elasticsearch_dsl import Search
from elastic.index import Index


class Store:

    __elastic: Elasticsearch
    __allow_duplicates: bool
    __index: Index

    def __init__(self, elastic, index: Index = None, allow_duplicates: bool = False):
        self.__elastic = elastic
        self.__allow_duplicates = allow_duplicates
        if index is not None:
            self.__index = index

    @property
    def allow_duplicates(self) -> bool:
        return self.__allow_duplicates

    @allow_duplicates.setter
    def allow_duplicates(self, flag: bool):
        self.__allow_duplicates = flag

    @property
    def index(self) -> Index:
        return self.__index

    @index.setter
    def index(self, i: Index):
        self.__index = i

    @property
    def elastic(self):
        return self.__elastic

    def list(self, entries: Generator) -> int:
        count = 0
        for e in entries:
            hits = 0
            try:
                if not self.allow_duplicates:
                    s = Search(using=self.elastic, index=self.index.from_kind(e.kind)).filter('term', hash=e.hash)
                    try:
                        result = s.execute()
                        hits = len(result.hits)
                    except NotFoundError:
                        pass
                if self.allow_duplicates or hits == 0:
                    self.elastic.index(index=self.index.from_kind(e.kind), body=e.to_dict())
                    count = count + 1
            except KeyError:
                pass   # if the kind is not there or not 0 or 1 (ie image or video), ignore
        return count

    def image_list(self, entries: Generator) -> int:
        self.index.map.pop(0)
        count = self.list(entries)
        self.index.image = self.index.image
        return count

    def video_list(self, entries: Generator) -> int:
        self.index.map.pop(1)
        count = self.list(entries)
        self.index.video = self.index.video
        return count

    def update(self, change, _id: str):
        self.__elastic.update(index=self.index, id=_id, body={'doc': change})
