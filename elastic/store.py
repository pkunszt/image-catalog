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

    def list(self, entries: Generator,
             destination_folder: str = "",
             name_from_captured_date: bool = False,
             name_from_modified_date: bool = False,
             keep_manual_names: bool = False) -> list:
        stored = []
        from_path = ""
        for e in entries:

            if e.kind not in (Constants.IMAGE_KIND, Constants.VIDEO_KIND, Constants.OTHER_KIND):
                raise StorageError(f"Invalid kind {str(e.kind)} in list for {e.name}")

            if not from_path:
                from_path = e.path
            elif e.path != from_path:
                raise StorageError(f"""Storing list from different dirs not allowed. 
                Until now we had {from_path} . Now the next item {e.name} has {e.path}""")

            original_path = e.full_path
            if destination_folder:
                e.path = destination_folder

            doc_to_store = e.to_dict()
            if name_from_captured_date or name_from_modified_date or keep_manual_names:
                self.set_name(doc_to_store, e, name_from_captured_date, name_from_modified_date, keep_manual_names)

            hits = 0
            if not self.allow_duplicates:
                # don't store if we have this already in our list of hashes we already stored
                if doc_to_store['path_hash'] in self.__path_hashes:
                    continue
                s = Search(using=self.elastic, index=self.index).filter('term', path_hash=doc_to_store['path_hash'])
                result = s.execute()
                hits = len(result.hits)
            if self.allow_duplicates or hits == 0:
                # avoid same name
                self.get_name(doc_to_store)
                try:
                    self.elastic.index(index=self.index, body=doc_to_store)
                except RequestError as e:
                    print("------------- Failed to store:-------------")
                    print(doc_to_store)
                    print(e)
                else:
                    if not self.allow_duplicates:
                        self.__path_hashes.add(doc_to_store['path_hash'])
                        self.__name_hashes.add(doc_to_store['hash'])
                    doc_to_store['original_path'] = original_path
                    stored.append(doc_to_store)
        return stored

    def get_name(self, doc_to_store):
        """If a file with the same name already exists, append a '_n' to the name to enumerate through"""
        name = doc_to_store['name']
        name_hash = doc_to_store['hash']
        while self.has_name(name_hash):
            n, e = os.path.splitext(name)
            prev_n = n.split("_")[-1]
            if not prev_n.isdigit() or len(prev_n) == len(n):
                n = n + '_1'
            else:
                n = "_".join(n.split("_")[0:-1]) + '_' + str(int(prev_n)+1)
            name = n + e
            name_hash = Entry.hash_from_name(os.path.join(doc_to_store['path'], name))
        doc_to_store['name'] = name
        doc_to_store['hash'] = name_hash

    def has_name(self, h: str) -> bool:
        if h in self.__name_hashes:
            return True
        s = Search(using=self.elastic, index=self.index).filter('term', hash=h)
        result = s.execute()
        return len(result.hits) > 0

    @staticmethod
    def set_name(doc_to_store, entry, name_from_captured_date, name_from_modified_date, keep_manual_names):
        name, ext = os.path.splitext(entry.name)
        changed = False
        if name_from_modified_date and hasattr(entry, "modified"):
            # modification time is only informative so much. Sometimes more info may be extracted later from
            # the original name, so append / keep it.
            doc_to_store['name'] = entry.modified_time_str + '@' + name + ext.lower()
            changed = True
        if (name_from_captured_date or name_from_modified_date) and hasattr(entry, "captured"):
            # if there is a captured date/time, use that, also for modification given
            doc_to_store['name'] = entry.captured_str + ext.lower()
            changed = True
        if keep_manual_names:
            # if there is significant text in the name already, keep that text, ignore numerals
            chars_only = "".join([
                c
                for c in name
                if ('A' <= c <= 'z') or c == ' '
            ])
            if len(chars_only)/len(name) > 0.5:
                doc_to_store['name'] = name
                if hasattr(entry, "captured"):
                    # but append the captured time to the text if there is one
                    doc_to_store['name'] += ' ' + entry.captured_str
                doc_to_store['name'] += ext.lower()
                changed = True
            elif hasattr(entry, "captured"):
                doc_to_store['name'] = entry.captured_str + ext.lower()
                changed = True
        if changed:
            doc_to_store['hash'] = Entry.hash_from_name(os.path.join(doc_to_store['path'], doc_to_store['name']))

    def update(self, change, _id: str):
        self.elastic.update(index=self.index, id=_id, body={'doc': change})
