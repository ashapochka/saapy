from saapy.graphdb import Neo4jClient
import pytest
import uuid


@pytest.fixture(scope="session")
def neo4j_client(request, workspace):
    url = workspace.get_resource_url("local_neo4j")
    user, password = workspace.get_resource_credentials("local_neo4j")
    client = Neo4jClient(url, user, password)
    client.connect()
    return client


@pytest.mark.skip(reason='no local neo4j installation assumed for this moment')
def test_run_in_tx(neo4j_client):
    def batch_job():
        query = """
        CREATE (tn: TestTempNode {name: {name}})
        """
        for i in range(50):
            params = dict(name=str(uuid.uuid4()))
            yield query, params

    result_set = neo4j_client.run_in_tx(batch_job(), chunk_count=16)
    assert len(result_set) == 50
