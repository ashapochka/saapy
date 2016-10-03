# coding=utf-8
from neo4j.v1 import GraphDatabase, basic_auth
# noinspection PyCompatibility
from collections.abc import Iterable, Generator
import sys
from typing import List
import logging
import requests
from string import Template

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

    import_nodes_template = Template("UNWIND {props} AS map "
                                     "CREATE (n$labels) SET n = map")

    def import_nodes(self, nodes: List[dict],
                     labels: List[str] = None,
                     chunk_size: int = 1000):
        node_labels = ':{0}'.format(':'.join(labels)) \
            if labels else ''
        query = self.import_nodes_template.safe_substitute(labels=node_labels)

        chunk_count = 1

        def batch():
            for i in range(0, len(nodes), chunk_size):
                logger.debug('starting chunk %s', i)
                result = (yield query, dict(props=nodes[i:i + chunk_size]))
                logger.debug(result)

        result = self.run_in_tx(batch(), chunk_count=chunk_count)
        return result

    def run_batch_query(self, query: str,
                        labels: List[str] = None,
                        params: List[dict] = None,
                        chunk_size: int = 1000):
        node_labels = ':{0}'.format(':'.join(labels)) \
            if labels else ''
        query_template = Template("UNWIND {params} AS params " + query)
        labeled_query = query_template.safe_substitute(labels=node_labels)

        chunk_count = 1

        def batch():
            for i in range(0, len(params), chunk_size):
                logger.debug('starting chunk %s', i)
                result = (yield labeled_query,
                                dict(params=params[i:i + chunk_size]))
                logger.debug(result)

        result = self.run_in_tx(batch(), chunk_count=chunk_count)
        return result

    def run_query(self, query: str, labels: List[str] = None, **kwargs) -> List:
        node_labels = ':{0}'.format(':'.join(labels)) \
            if labels else ''
        query_template = Template(query)
        labeled_query = query_template.safe_substitute(labels=node_labels)
        logger.debug('will run query %s', labeled_query)

        def batch():
            yield labeled_query, kwargs

        result = self.run_in_tx(batch(), chunk_count=1)
        return result[0]

    def set_neo4j_password(self, new_password):
        """
        sets new password for the neo4j server updating the server

        :param new_password: new password to set
        :return: boolean: True if update is successful

        An excerpt from neo4j documentation on password change API:

        Changing the user password
        Given that you know the current password, you can ask the server to
        change a users password.
        You can choose any password you like, as long as it is different from
        the current password.

        Example request

        POST http://localhost:7474/user/neo4j/password
        Accept: application/json; charset=UTF-8
        Authorization: Basic bmVvNGo6bmVvNGo=
        Content-Type: application/json
        {
          "password" : "secret"
        }
        Example response

        200: OK
        """

        value_error_msg = ''

        if new_password == self.neo4j_password:
            value_error_msg = "New password must not equal old password"
        elif not new_password:
            value_error_msg = "New password must not be empty"

        if value_error_msg:
            raise ValueError(value_error_msg)

        url = "{host_url}/user/{user_name}/password".format(
            host_url=self.neo4j_url, user_name=self.neo4j_user)
        headers = {"Accept": "application/json; charset=UTF-8",
                   "Content-Type": "application/json"}
        payload = {'password': new_password}
        r = requests.post(url, auth=(self.neo4j_user, self.neo4j_password),
                          headers=headers, json=payload)
        if r.ok:
            self.neo4j_password = new_password
            return True
        else:
            r.raise_for_status()
