# coding=utf-8
from neo4j.v1 import GraphDatabase, basic_auth
from collections.abc import Iterable, Generator
import sys
from typing import List
import logging


logger = logging.getLogger(__name__)


class Neo4jClient:
    def __init__(self, neo4j_url, user, password):
        self.neo4j_url = neo4j_url
        self.neo4j_user = user
        self.neo4j_password = password
        self.neo4j_driver = None

    def connect(self):
        self.neo4j_driver = GraphDatabase.driver(
            self.neo4j_url,
            auth=basic_auth(self.neo4j_user, self.neo4j_password))
        return self.neo4j_driver

    def run_in_tx(self, batch, chunk_count=None, dry_run=False):
        if not chunk_count:
            chunk_count = sys.maxsize
        if isinstance(batch, Generator):
           it = batch
        elif isinstance(batch, Iterable):
            def gen():
                for j in batch:
                    yield j
            it = gen()
        else:
            err = "batch_job must be iterable or callable but {0} passed"
            err = err.format(type(batch))
            logger.error(err)
            raise ValueError(err)
        if dry_run:
            return list(it)
        session = self.neo4j_driver.session()
        try:
            result_set = []
            consumed_result = None
            more_chunks = True
            while more_chunks:
                logger.debug('neo4j transaction beginning')
                with session.begin_transaction() as tx:
                    chunk_i = 0
                    try:
                        while chunk_i < chunk_count:
                            # noinspection PyNoneFunctionAssignment
                            query, params = it.send(consumed_result)
                            logger.debug('chunk %s will run query %s'
                                         'in transaction', chunk_i, query)
                            result = tx.run(query, params)
                            consumed_result = list(result)
                            result_set.append(consumed_result)
                            chunk_i += 1
                    except StopIteration:
                        more_chunks = False
                    tx.success = True
                logger.debug('neo4j transaction committed')
            return result_set
        finally:
            session.close()

    def import_nodes(self, nodes: List[dict],
                     chunk_size: int = 1000, labels: List[str] = []):
        node_labels = ':{0}'.format(':'.join(labels)) \
            if labels else ''
        query = "UNWIND {props} AS map " + \
                "CREATE (n{labels}) SET n = map".format(labels=node_labels)

        chunk_count = 1

        def batch():
            for i in range(0, len(nodes), chunk_size):
                logger.debug('starting chunk %s', i)
                result = (yield query, dict(props=nodes[i:i + chunk_size]))
                logger.debug(result)

        self.run_in_tx(batch(), chunk_count=chunk_count)

    def run_query(self, query: str, labels: List[str] = [], **kwargs) -> List:
        node_labels = ':{0}'.format(':'.join(labels)) \
            if labels else ''
        labeled_query = query.format(labels=node_labels)
        logger.debug('will run query %s', labeled_query)

        def batch():
            yield labeled_query, kwargs

        result = self.run_in_tx(batch(), chunk_count=1)
        return result
