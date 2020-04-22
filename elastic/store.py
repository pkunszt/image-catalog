from typing import Generator
from elasticsearch import Elasticsearch, RequestError
from elasticsearch_dsl import Search

from data import Entry
from elastic.connection import Connection
from constants import Constants
import os


class StorageError(ValueError):
    def __init__(self, message: str):
        super().__init__(message)


class Store:

    __elastic: Elasticsearch
    __allow_duplicates: bool
    __index: str
    __path_hashes: set
    __name_hashes: set

    def __init__(self, connection: Connection, allow_duplicates: bool = False):
        self.__elastic = connection.get()
        self.__index = connection.index
        self.__allow_duplicates = allow_duplicates
        self.__path_hashes = set()
        self.__name_hashes = set()

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

    def list(self, entries: Generator) -> list:
        stored = []
        self.__path_hashes.clear()
        self.__name_hashes.clear()
        for e in entries:
            if e.kind not in (Constants.IMAGE_KIND, Constants.VIDEO_KIND, Constants.OTHER_KIND):
                raise StorageError(f"Invalid kind {str(e.kind)} in list for {e.name}")

            hits = 0
            if not self.allow_duplicates:
                # don't store if we have this already in our list of hashes we already stored. path_hash = path+checksum
                if e.path_hash in self.__path_hashes:
                    continue
                s = Search(using=self.elastic, index=self.index).filter('term', path_hash=e.path_hash)
                result = s.execute()
                hits = len(result.hits)
            if self.allow_duplicates or hits == 0:
                # avoid same name
                self.get_name(e)
                try:
                    self.elastic.index(index=self.index, body=e.to_dict())
                except RequestError as err:
                    print("------------- Failed to store:-------------")
                    print(e.to_dict())
                    print(err)
                else:
                    if not self.allow_duplicates:
                        self.__path_hashes.add(e.path_hash)
                        self.__name_hashes.add(e.hash)
                    stored.append(e)
        return stored

    def get_name(self, entry):
        """If a file with the same name already exists, append a '_n' to the name to enumerate through"""
        name = entry.name
        name_hash = entry.hash
        while self.has_name(name_hash):
            n, e = os.path.splitext(name)
            prev_n = n.split("_")[-1]
            if not prev_n.isdigit() or len(prev_n) == len(n):
                n = n + '_1'
            else:
                n = "_".join(n.split("_")[0:-1]) + '_' + str(int(prev_n)+1)
            name = n + e
            name_hash = Entry.hash_from_name(os.path.join(entry.path, name))
        entry.name = name

    def has_name(self, h: str) -> bool:
        if h in self.__name_hashes:
            return True
        s = Search(using=self.elastic, index=self.index).filter('term', hash=h)
        result = s.execute()
        return len(result.hits) > 0

    def update(self, change, _id: str):
        self.elastic.update(index=self.index, id=_id, body={'doc': change})
