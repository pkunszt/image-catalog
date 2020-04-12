from elastic.connection import Connection
from elasticsearch import Elasticsearch
from typing import List


class StorageError(EnvironmentError):
    def __init__(self, message: str):
        super().__init__(message)


class Delete:
    __connection: Connection

    def __init__(self, connection: Connection = None):
        self.__connection = connection

    @property
    def elastic(self) -> Elasticsearch:
        return self.__connection.get()

    @property
    def connection(self):
        return self.__connection

    @connection.setter
    def connection(self, con: Connection):
        self.__connection = con

    def delete_id(self, index: str, _id: str) -> None:
        result = self.elastic.delete(index=index, id=_id)
        if result['result'] != 'deleted':
            raise StorageError("Failed Delete " + result['result'])

    def delete_id_list(self, index: str, array_of_ids: List[str]) -> int:
        result = self.elastic.delete_by_query(index=index, body={"query": {"ids": {"values": array_of_ids}}})
        if len(result['failures']) > 0:
            raise StorageError("Failed Delete " + result['failures'])
        if result['deleted'] != len(array_of_ids):
            err_str = "Failed Delete: expected "+str(len(array_of_ids))+" got "+str(result['deleted'])
            raise StorageError(err_str)
        return result['deleted']
