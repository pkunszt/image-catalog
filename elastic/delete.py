from elastic.connection import Connection
from elasticsearch import Elasticsearch
from typing import List


class StorageError(EnvironmentError):
    def __init__(self, message: str):
        super().__init__(message)


class Delete:
    __connection: Connection

    def __init__(self, connection: Connection):
        self.__connection = connection

    @property
    def elastic(self) -> Elasticsearch:
        return self.__connection.get()

    @property
    def index(self) -> str:
        return self.__connection.index

    def id(self, _id: str) -> None:
        result = self.elastic.delete(index=self.index, id=_id)
        if result['result'] != 'deleted':
            raise StorageError("Failed Delete " + result['result'])

    def id_list(self, array_of_ids: List[str]) -> int:
        result = self.elastic.delete_by_query(index=self.index, body={"query": {"ids": {"values": array_of_ids}}})
        if len(result['failures']) > 0:
            raise StorageError("Failed Delete " + result['failures'])
        if result['deleted'] != len(array_of_ids):
            err_str = "Failed Delete: expected "+str(len(array_of_ids))+" got "+str(result['deleted'])
            raise StorageError(err_str)
        return result['deleted']

    def checksum(self, checksum: str) -> int:
        result = self.elastic.delete_by_query(index=self.index, body={"query": {"term": {"checksum": checksum}}})
        if len(result['failures']) > 0:
            raise StorageError("Failed Delete " + result['failures'])
        return result['deleted']
