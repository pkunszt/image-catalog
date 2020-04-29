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
    __not_stored_count: int

    def __init__(self, connection: Connection, allow_duplicates: bool = False):
        self.__elastic = connection.get()
        self.__index = connection.index
        self.__allow_duplicates = allow_duplicates
        self.__path_hashes = set()
        self.__name_hashes = set()
        self.__checksums = set()
        self.__not_stored_count = 0

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

    def list(self, entries: Generator, dryrun: bool = False) -> list:
        stored = []
        self.__not_stored_count = 0
        for e in entries:
            if e.kind not in (Constants.IMAGE_KIND, Constants.VIDEO_KIND, Constants.OTHER_KIND):
                raise StorageError(f"Invalid kind {str(e.kind)} in list for {e.name}")
            if e.check_if_in_catalog and ((e.checksum in self.__checksums) or self.has_checksum(e.checksum)):
                # a file with this checksum has already been uploaded into the catalog.
                self.__not_stored_count += 1
                continue
            if not self.allow_duplicates and ((e.path_hash in self.__path_hashes) or self.has_path_hash(e.path_hash)):
                # don't store if we have this already in our list of hashes we already stored. path_hash = path+checksum
                self.__not_stored_count += 1
                continue

            # avoid same name
            self.get_name(e)
            try:
                if not dryrun:
                    self.elastic.index(index=self.index, body=e.to_dict())
            except RequestError as err:
                print("------------- Failed to store:-------------")
                print(e.to_dict())
                print(err)
                self.__not_stored_count += 1
            else:
                if not self.allow_duplicates:
                    self.__path_hashes.add(e.path_hash)
                    self.__name_hashes.add(e.hash)
                    self.__checksums.add(e.checksum)
                stored.append(e)

        return stored

    def has_path_hash(self, path_hash) -> bool:
        s = Search(using=self.elastic, index=self.index).filter('term', path_hash=path_hash)
        result = s.execute()
        hits = len(result.hits)
        return hits > 0

    def has_checksum(self, checksum) -> bool:
        s = Search(using=self.elastic, index=self.index).filter('term', checksum=checksum)
        result = s.execute()
        hits = len(result.hits)
        return hits > 0

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

    @property
    def not_stored(self):
        return self.__not_stored_count
