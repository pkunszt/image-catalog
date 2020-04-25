from data import Factory
from elastic.connection import Connection
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, A


class Retrieve:
    __connection: Connection

    def __init__(self, connection: Connection):
        self.__connection = connection

    @property
    def elastic(self) -> Elasticsearch:
        return self.__connection.get()

    @property
    def index(self) -> str:
        return self.__connection.index

    def all_ids(self):
        s = Search(using=self.elastic, index=self.index)
        for entry in s.scan():
            yield entry.meta.id

    def get_by_id(self, _id: str):
        result = self.elastic.get(index=self.index, id=_id)
        # note: can add _source_includes=['path', 'name'] to restrict the result set
        return result['_source']

    def all_entries(self, directory_filter: str = None):
        s = Search(using=self.elastic, index=self.index)
        if directory_filter is not None:
            s = s.filter('match_phrase', path=directory_filter)
        for entry in s.scan():
            yield entry

    def all_paths(self):
        """
        Generator that just iterates through all paths in index.
        """
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
            s = Search(using=self.elastic, index=self.index).extra(size=0)
            path_aggregation = A('terms', field='path.keyword', size=999999,
                                 include={"partition": i, "num_partitions": partitions})
            s.aggs.bucket('paths', path_aggregation)
            result = s.execute()
            for path in result.aggregations.paths.buckets:
                yield path.key
            i = i + 1

    def on_nas_but_not_on_dropbox(self, limit: int = 0):
        s = Search.from_dict({
            "query": {
                "bool": {
                    "must_not": {"exists": {"field": "dropbox"}},
                    "filter": {"term": {"nas": "true"}}
                    }
                }
            })
        s = s.using(self.elastic).index(self.index)
        if limit:
            s = s[:limit]
        result = s.execute()
        for e in result.hits:
            yield Factory.from_elastic_entry(e)
