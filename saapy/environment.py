from .clients import SonarClient
from .clients import Neo4jClient
from .clients import GitClient
from .clients import ScitoolsClient
from .clients import JiraClient


class Environment:
    def __init__(self, ws, name=None):
        self.ws = ws
        if not name:
            self.name = self.ws.configuration["active_env"]
        self.services = {}
        self.service_connectors = dict(
            neo4j_service=connect_neo4j,
            sonar_service=connect_sonar,
            git_local_service=connect_git,
            scitools_local_service=connect_scitools,
            jira_service=connect_jira
        )

    def setup(self):
        service_refs = self.ws.configuration[self.name]["services"]
        for sr in service_refs:
            service_key = list(sr.keys())[0]
            service_name = sr[service_key]
            service_type = self.ws.get_service_type(service_name)
            connector = self.service_connectors[service_type]
            service = connector(self.ws, service_name)
            self.services[service_key] = service

    def __getattr__(self, item):
        return self.services[item]


def connect_sonar(ws, service_name):
    sonar_url = ws.get_service_url(service_name)
    sonar_token_name, sonar_token = ws.get_service_credentials(service_name)
    sonar = SonarClient(sonar_url, sonar_token)
    return sonar


def connect_neo4j(ws, service_name):
    url = ws.get_service_url(service_name)
    user, password = ws.get_service_credentials(service_name)
    client = Neo4jClient(url, user, password)
    client.connect()
    return client


def connect_git(ws, service_name):
    if "git_local_service" == ws.get_service_type(service_name):
        git_path = ws.get_service_path(service_name, resolve_relative=True)
        client = GitClient(git_path)
        client.connect()
        return client
    else:
        return None


def connect_scitools(ws, service_name):
    if "scitools_local_service" == ws.get_service_type(service_name):
        udb_path = ws.get_service_path(service_name, resolve_relative=True)
        client = ScitoolsClient(udb_path)
        client.connect()
        return client
    else:
        return None


def connect_jira(ws, service_name):
    url = ws.get_service_url(service_name)
    user, password = ws.get_service_credentials(service_name)
    jira = JiraClient(url, user, password)
    jira.connect()
    return jira
