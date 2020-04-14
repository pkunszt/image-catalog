from elasticsearch import Elasticsearch
from elasticsearch_dsl import connections


class Connection:
    """Class to store json data in elastic"""
    __elastic: Elasticsearch
    __connection: connections.Connections
    __duplicate_dict: dict
    __host: str
    __port: int
    __index: str

    # The connection is a static class variable, reused every time
    __connection = connections.Connections()

    def __init__(self, host: str = None, port: int = None):
        self.__duplicate_dict = {}
        self.host = host if host else 'localhost'
        self.port = port if port else 9200
        self.index = 'catalog'

    @property
    def host(self) -> str:
        return self.__host

    @property
    def port(self) -> int:
        return self.__port

    @property
    def index(self) -> str:
        return self.__index

    @property
    def connection_name(self) -> str:
        return self.index + self.host + str(self.port)

    @host.setter
    def host(self, host: str):
        self.__host = host

    @port.setter
    def port(self, port: int):
        self.__port = port

    @index.setter
    def index(self, i: str):
        self.__index = i

    def get(self) -> Elasticsearch:
        """The connection is reused. On first try there will be no 'elastic' connection. Create it.
        Will create different connections for each host:port combination, by using that in the name."""

        try:
            self.__elastic = type(self).__connection.get_connection(self.connection_name)
        except KeyError:
            type(self).__connection.configure(**{self.connection_name: {'hosts': [self.__host + ':' + str(self.__port)]}})
            return self.get()

        return self.__elastic

    def close(self) -> None:
        """Force closing connection to elastic on given host and port. Only use if you know what you are doing"""
        try:
            type(self).__connection.get_connection(self.connection_name)
        except KeyError:
            return
        type(self).__connection.remove_connection(self.connection_name)
        print("closed connection to "+self.host+':'+str(self.port))
