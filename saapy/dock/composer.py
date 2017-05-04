# coding=utf-8
from saapy.graphdb import DockNeo4j


class DockProject:
    """
    Creates docker-compose files for the entire project
    """

    project_name = None
    target_dir = None

    def __init__(self, project_name, target_dir):
        self.project_name = project_name
        self.target_dir = target_dir

    def compose(self):
        dock_neo = DockNeo4j(self.project_name)
