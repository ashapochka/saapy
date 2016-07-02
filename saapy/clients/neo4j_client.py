from neo4j.v1 import GraphDatabase, basic_auth
from collections import Iterable, Callable
import sys


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

    def run_in_tx(self, batch_job, chunk_size=None, dry_run=False):
        if not chunk_size:
            chunk_size = sys.maxsize
        if isinstance(batch_job, Iterable):
            def job():
                for j in batch_job:
                    yield j
        elif isinstance(batch_job, Callable):
            job = batch_job
        else:
            err = "batch_job can be iterable or callable while {0} passed"
            err = err.format(type(batch_job))
            raise ValueError(err)
        if dry_run:
            return list(job())
        session = self.neo4j_driver.session()
        try:
            result_set = []
            it = job()
            consumed_result = None
            more_chunks = True
            while more_chunks:
                with session.begin_transaction() as tx:
                    chunk_i = 0
                    try:
                        while chunk_i < chunk_size:
                            # noinspection PyNoneFunctionAssignment
                            query, params = it.send(consumed_result)
                            result = tx.run(query, params)
                            consumed_result = list(result)
                            result_set.append(consumed_result)
                            chunk_i += 1
                    except StopIteration:
                        more_chunks = False
                    tx.success = True
            return result_set
        finally:
            session.close()
