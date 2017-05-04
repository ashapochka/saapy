# coding=utf-8

import yaml


class DockNeo4j:
    """
    generates Docker related configuration for neo4j
    """

    image_name = 'saapy/graph-database'
    project_name = None
    network_address = None

    def __init__(self, project_name, network_address=None):
        self.project_name = project_name
        self.network_address = network_address

    def compose_neo4j_service(self):
        """
        builds neo4j service definition for docker-compose
        """
        service = dict()
        service['image'] = self.image_name
        service['ports'] = self.ports()
        service['volumes'] = self.volumes()
        service['ulimits'] = {'nofile': {'soft': 40000,
                                         'hard': 40000}}
        if self.network_address:
            service['networks'] = {
                self.network_address[0]: dict(
                    ipv4_address=self.network_address[1])}
        return service

    def ports(self):
        """
        :return: neo4j port mappings
        """
        return ['7473:7473', '7474:7474', '7687:7687']

    def volumes(self):
        """
        :return: neo4j volume mappings
        """
        return ['{0}_{1}:/{1}'.format(self.project_name, volume)
                for volume in ['data', 'conf', 'ssl']]


def test_compose():
    dock = DockNeo4j('dummyprj')
    service = dock.compose_neo4j_service()
    print()
    print(yaml.dump(service, default_flow_style=False, indent=4))


def test_compose_net():
    dock = DockNeo4j('dummyprj', network_address=('dummynet', '10.0.0.2'))
    service = dock.compose_neo4j_service()
    print()
    print(yaml.dump(service, default_flow_style=False, indent=4))
