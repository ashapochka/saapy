# coding=utf-8
from concurrent.futures import ThreadPoolExecutor
from typing import List
from toolz import juxt
from itertools import repeat

from saapy.graphdb import Neo4jClient


class Neo4jAbstractQuery:
    def __init__(self, labels=()):
        self.labels = labels

    def __call__(self, neo_client):
        raise NotImplementedError()


class Neo4jImportQuery(Neo4jAbstractQuery):
    def __init__(self,
                 query_params: List[dict] = (),
                 chunk_size: int = 1000, **kwargs):
        self.query_params = query_params
        self.chunk_size = chunk_size
        super().__init__(**kwargs)

    def __call__(self, neo4j_client: Neo4jClient):
        result = neo4j_client.import_nodes(self.query_params,
                                           labels=self.labels,
                                           chunk_size=self.chunk_size)
        return result


class Neo4jBatchQuery(Neo4jAbstractQuery):
    def __init__(self, query_text: str,
                 query_params: List[dict]=None,
                 chunk_size: int = 1000, **kwargs):
        if query_params is None:
            query_params = []
        self.query_text = query_text
        self.query_params = query_params
        self.chunk_size = chunk_size
        super().__init__(**kwargs)

    def __call__(self, neo4j_client: Neo4jClient):
        result = neo4j_client.run_batch_query(self.query_text,
                                              labels=self.labels,
                                              params=self.query_params,
                                              chunk_size=self.chunk_size)
        return result


class Neo4jGenericQuery(Neo4jAbstractQuery):
    def __init__(self, query_text: str, query_params: dict=None, **kwargs):
        if query_params is None:
            query_params = dict()
        self.query_text = query_text
        self.query_params = query_params
        super().__init__(**kwargs)

    def __call__(self, neo4j_client: Neo4jClient):
        result = neo4j_client.run_query(self.query_text,
                                        labels=self.labels,
                                        params=self.query_params)
        return result


class Neo4jQueryFactory:
    def __init__(self, default_labels=()):
        self.default_labels = default_labels

    def query(self,
              query_text: str,
              labels=(),
              query_params: dict=None,
              **kwargs):
        return Neo4jGenericQuery(query_text,
                                 labels=self.default_labels + labels,
                                 query_params=query_params,
                                 **kwargs)

    def import_query(self,
                     labels=(),
                     query_params: List[dict]=None,
                     chunk_size: int = 1000,
                     **kwargs):
        return Neo4jImportQuery(labels=self.default_labels + labels,
                                query_params=query_params,
                                chunk_size=chunk_size,
                                **kwargs)

    def batch_query(self,
                    query_text: str,
                    labels=(),
                    query_params: List[dict]=None,
                    chunk_size: int = 1000,
                    **kwargs):
        return Neo4jBatchQuery(query_text,
                               labels=self.default_labels + labels,
                               query_params=query_params,
                               chunk_size=chunk_size,
                               **kwargs)


class Neo4jQueryInvoker:
    def __init__(self, neo4j_client: Neo4jClient):
        self.neo4j_client = neo4j_client

    def run(self, *queries: Neo4jAbstractQuery):
        results = juxt(*queries)(self.neo4j_client)
        if len(results) > 1:
            return results
        elif len(results) == 1:
            return results[0]
        else:
            return None


class Neo4jQueryAsyncInvoker(Neo4jQueryInvoker):
    def __init__(self,
                 neo4j_client: Neo4jClient,
                 max_workers: int = None):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        super().__init__(neo4j_client)

    def run(self, *queries: Neo4jAbstractQuery):
        fs = list(map(self.executor.submit,
                      queries,
                      repeat(self.neo4j_client)))
        if len(fs) > 1:
            return fs
        elif len(fs) == 1:
            return fs[0]
        else:
            return None
