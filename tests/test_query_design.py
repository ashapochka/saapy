# coding=utf-8
from concurrent.futures import ThreadPoolExecutor
from typing import List

import pytest
from unittest.mock import MagicMock
from saapy.connectors.neo4j import *


class DummyQueryFactory(Neo4jQueryFactory):
    def count_nodes_query(self):
        return self.query("MATCH (n) RETURN COUNT(n)",
                          labels=('l1',))

    def connect_nodes_query(self):
        return self.batch_query("CREATE (n)-[r]->(m)",
                                labels=('l1',),
                                query_params=[])

    def create_nodes_query(self):
        return self.import_query(labels=('l1',),
                                 query_params=[])


@pytest.fixture
def query_factory():
    return DummyQueryFactory(default_labels=('test',))


@pytest.fixture
def neo4j_client():
    return MagicMock(spec=Neo4jClient)


@pytest.fixture
def async_invoker(neo4j_client):
    return Neo4jQueryAsyncInvoker(neo4j_client)


def test_abstract_base_query():
    with pytest.raises(NotImplementedError):
        abstract_query = Neo4jAbstractQuery()
        abstract_query(None)


def test_generic_query(query_factory, neo4j_client):
    count_nodes = query_factory.count_nodes_query()
    count_nodes(neo4j_client)
    assert neo4j_client.run_query.called
    assert neo4j_client.run_query.call_args[0][0] == \
           "MATCH (n) RETURN COUNT(n)"
    assert neo4j_client.run_query.call_args[1]['labels'] == ('test', 'l1')


def test_batch_query(query_factory, neo4j_client):
    connect_nodes = query_factory.connect_nodes_query()
    connect_nodes(neo4j_client)
    assert neo4j_client.run_batch_query.called
    assert neo4j_client.run_batch_query.call_args[0][0] == "CREATE (n)-[r]->(m)"
    assert neo4j_client.run_batch_query.call_args[1]['labels'] == ('test', 'l1')
    assert neo4j_client.run_batch_query.call_args[1]['chunk_size'] == 1000
    assert neo4j_client.run_batch_query.call_args[1]['params'] == []


def test_import_query(query_factory, neo4j_client):
    create_nodes = query_factory.create_nodes_query()
    create_nodes(neo4j_client)
    assert neo4j_client.import_nodes.called
    assert neo4j_client.import_nodes.call_args[0][0] == []
    assert neo4j_client.import_nodes.call_args[1]['labels'] == ('test', 'l1')
    assert neo4j_client.import_nodes.call_args[1]['chunk_size'] == 1000


def test_async_query(query_factory, neo4j_client, async_invoker):
    count_nodes = query_factory.count_nodes_query()
    future = async_invoker.run(count_nodes)
    future.result(timeout=1)
    assert neo4j_client.run_query.called
