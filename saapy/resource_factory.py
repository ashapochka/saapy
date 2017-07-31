from .codetools import SonarClient
from .graphdb import Neo4jClient
from saapy.vcs import GitClient
from .codetools import ScitoolsClient
from .issue import JiraClient


class ResourceFactory:
    def __init__(self):
        self.resource_factory_methods = dict(
            neo4j_service=create_neo4j,
            sonar_service=create_sonar,
            git_local_service=create_git,
            scitools_local_service=create_scitools,
            jira_service=create_jira,
            secret_store=create_secret_store
        )

    def create_resource(self, workspace, resource_name, resource_conf):
        resource_type = resource_conf['resource_type']
        factory_method = self.resource_factory_methods[resource_type]
        resource_impl = factory_method(workspace, resource_name)
        return resource_impl


def create_sonar(ws, resource_name):
    sonar_url = ws.get_resource_url(resource_name)
    sonar_token_name, sonar_token = ws.get_resource_credentials(resource_name)
    sonar = SonarClient(sonar_url, sonar_token)
    return sonar


def create_neo4j(ws, resource_name):
    url = ws.get_resource_url(resource_name)
    user, password = ws.get_resource_credentials(resource_name)
    client = Neo4jClient(url, user, password)
    return client


def create_git(ws, resource_name):
    if "git_local_service" == ws.get_resource_type(resource_name):
        git_path = ws.get_resource_path(resource_name, resolve_relative=True)
        client = GitClient(git_path)
        return client
    else:
        return None


def create_scitools(ws, resource_name):
    if "scitools_local_service" == ws.get_resource_type(resource_name):
        udb_path = ws.get_resource_path(resource_name, resolve_relative=True)
        client = ScitoolsClient(udb_path)
        return client
    else:
        return None


def create_jira(ws, resource_name):
    url = ws.get_resource_url(resource_name)
    user, password = ws.get_resource_credentials(resource_name)
    jira = JiraClient(url, user, password)
    return jira


def create_secret_store(ws, resource_name):
    return None
