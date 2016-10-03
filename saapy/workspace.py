# coding=utf-8


from pathlib import Path
import shutil
import time
import yaml
from string import Template
import os
from .secret_store import SecretStore
from .resource_factory import ResourceFactory


class Workspace:
    """
    represents an assessment workspace including local work directory
    with analyzed files.
    """

    def __init__(self,
                 configuration_path,
                 override_configuration=None,
                 **kwargs):
        self.conf_file = Path(configuration_path)
        if override_configuration:
            self.__configuration = override_configuration
            self.__resolved_conf = resolve_configuration_template(
                self.__configuration, **kwargs)
        else:
            self.load_configuration(**kwargs)
        self.name = self.conf('workspace', 'name')
        self.work_dir = Path(self.conf('workspace', 'work_directory'))
        self.work_dir.mkdir(exist_ok=True)
        self.secret_store = self._init_secret_store()
        self.resource_factory = ResourceFactory()
        self.resources = {key: Resource(self, key, value)
                          for key, value in self.conf('resources').items()}
        self.projects = {key: Project(self, key, value)
                         for key, value in self.conf('projects').items()}

    def _init_secret_store(self):
        store_name = self.conf('workspace', 'secret_store')
        store_type = self.conf('resources', store_name, 'store_type')
        if store_type == 'fernet_yaml_store':
            master_key_file = self.conf('resources', store_name,
                                        'master_key_file')
            self._secret_file = self.conf('resources', store_name,
                                          'secret_file')
            store = SecretStore.load_from_yaml(master_key_file,
                                               self._secret_file)
            return store
        else:
            raise Exception('Unsupported secret store type {0}'.format(
                store_type))

    def __str__(self):
        return "<Workspace name='{0}' work_dir={1}>".format(self.name,
                                                            self.work_dir)

    @classmethod
    def load_from_home(cls, relative_conf_path, **kwargs):
        """
        loads workspace relative to the user directory
        :param relative_conf_path: path to configuration
        relative to the user directory
        :return: initialized workspace
        """
        return cls(Path.home() / relative_conf_path,
                   override_configuration=None, **kwargs)

    @classmethod
    def load_from_wd(cls, relative_conf_path='conf/workspace.yml', **kwargs):
        """
        loads workspace relative to the current directory
        :param relative_conf_path: path to configuration
        relative to the current directory
        :return: initialized workspace
        """
        work_directory = str(Path('.').resolve())
        return cls(Path(".") / relative_conf_path,
                   override_configuration=None,
                   SAAPY_WORK_DIR=work_directory,
                   **kwargs)

    @classmethod
    def create_from_template(cls, configuration_path, **kwargs):
        with open(configuration_path, 'w') as yaml_file:
            dump_configuration(yaml_file, **kwargs)
        return cls(configuration_path,
                   override_configuration=None, **kwargs)

    def touch(self, filename):
        filepath = self.work_dir / filename
        filepath.touch()
        return filepath

    def mkdir(self, dirname):
        dirpath = self.work_dir / dirname
        dirpath.mkdir(parents=True, exist_ok=True)
        return dirpath

    def archive(self):
        timestr = time.strftime("%Y%m%d-%H%M%S")
        archive_name = "{0}_{1}".format(self.work_dir, timestr)
        shutil.make_archive(archive_name, "zip",
                            str(self.local_root_dir),
                            str(self.work_dir.name))

    def abs_path(self, filepath):
        return self.work_dir / filepath

    def abs_path_str(self, filepath):
        return str(self.abs_path(filepath))

    def conf(self, *path):
        conf_level = self.__resolved_conf
        for key in path:
            conf_level = conf_level[key]
        return conf_level

    # def update_configuration(self, update_dict):
    #     self.__configuration.update(update_dict)
    #
    # def update_resource_conf(self, resource, resource_conf, password=None):
    #     self.update_configuration({resource: resource_conf})
    #     if password and "user_name" in resource_conf:
    #         self.secret_store.set_secret(password, resource,
    #                                      resource_conf["user_name"])

    def get_resource_credentials(self, resource):
        try:
            user = self.conf('resources', resource, "user_name")
            if user:
                path = [resource, user]
            else:
                path = [resource]
            secret = self.secret_store.get_secret(*path)
            decoded_secret = str(secret, 'utf-8')
            return user, decoded_secret
        except KeyError:
            return None, None

    def get_resource_url(self, resource):
        url = self.conf('resources', resource, "resource_url")
        return url

    def get_resource_path(self, resource, resolve_relative=False):
        path = self.conf('resources', resource, "resource_path")
        if resolve_relative:
            path = self.abs_path_str(path)
        return path

    def get_resource_type(self, resource):
        return self.conf('resources', resource, "resource_type")

    def get_resource_user(self, resource):
        return self.conf('resources', resource, "user_name")

    def project(self, name):
        return self.projects[name]

    def resource(self, name):
        return self.resources[name]

    def save_configuration(self):
        with open(str(self.conf_file), 'w') as yaml_file:
            yaml.dump(self.__configuration, yaml_file, default_flow_style=False)
        self.secret_store.save_as_yaml(self._secret_file)

    def load_configuration(self, **kwargs):
        with open(str(self.conf_file), 'r') as yaml_file:
            self.__configuration = yaml.load(yaml_file)
            self.__resolved_conf = resolve_configuration_template(
                self.__configuration, **kwargs)


class Project:
    def __init__(self, workspace, name, conf):
        self.workspace = workspace
        self.name = name
        self.conf = conf
        self.resources = {res_name: self.workspace.resource(res_name)
                          for res_name in self.conf['resources']}

    def resource(self, name):
        return self.resources[name]


class Resource:
    def __init__(self, workspace, name, conf):
        self.workspace = workspace
        self.name = name
        self.conf = conf
        self.impl = self.workspace.resource_factory.create_resource(
            self.workspace,
            self.name,
            self.conf
        )
        self.connected = False

    def connect(self):
        if not self.connected:
            self.impl.connect()
            self.connected = True


def configuration_template():
    """
    builds default configuration template with values to substitute
    using string.Template $ format, so they can be replaced from os.environ
    or similar dictionary
    :return: template as dict of dicts and lists
    """
    template = {
        'workspace': {
            'name': '$SAAPY_WS_NAME',
            'work_directory': '$SAAPY_WORK_DIRECTORY',
            'secret_store': 'secret_store_default'
        },
        'projects': {
            '$SAAPY_PROJECT_NAME': {
                'resources': [
                    'neo4j_default',
                    'scitools_default',
                    'git_default'
                ]
            }
        },
        'resources': {
            'neo4j_default': {
                'resource_type': 'neo4j_service',
                'resource_url': '$SAAPY_NEO4J_URL',
                'user_name': '$SAAPY_NEO4J_USER'
            },
            'secret_store_default': {
                'resource_type': 'secret_store',
                'store_type': 'fernet_yaml_store',
                'master_key_file': '$SAAPY_MASTER_KEY_FILE',
                'secret_file': '$SAAPY_SECRET_FILE',
            },
            'git_default': {
                'resource_type': 'git_local_service',
                'resource_path': '$SAAPY_GIT_REPOSITORY'
            },
            'scitools_default': {
                'resource_type': 'scitools_local_service',
                'resource_path': '$SAAPY_SCITOOLS_FILE'
            },
            'jira_default': {
                'resource_type': 'jira_service',
                'resource_url': '$SAAPY_JIRA_URL',
                'user_name': '$SAAPY_JIRA_USER'
            },
            'sonar_default': {
                'resource_type': 'sonar_service',
                'resource_url': '$SAAPY_SONAR_URL',
                'user_name': '$SAAPY_SONAR_USER'
            }
        }
    }
    return template


class ConfTemplate(Template):
    idpattern = r'[_a-z][\._a-z0-9]*'


def resolve_configuration_template(template: dict, **kwargs):
    def resolve_str(value: str, vars: dict):
        t = ConfTemplate(value)
        return t.safe_substitute(**vars)

    def resolve(struct, vars:dict):
        if isinstance(struct, dict):
            return {resolve_str(key, vars): resolve(value, vars)
                    for key, value in struct.items()}
        elif isinstance(struct, list):
            return [resolve(value, vars) for value in struct]
        elif isinstance(struct, str):
            return resolve_str(struct, vars)
        else:
            raise ValueError(
                'Value has unresolvable type {0}'.format(type(struct)))

    def flatten_template(struct, target, prefix=""):
        if isinstance(struct, dict):
            for key, value in struct.items():
                key_prefix = prefix + '.' + key if prefix else key
                flatten_template(value, target, prefix=key_prefix)
        elif isinstance(struct, list):
            for i, value in enumerate(struct):
                i_prefix = prefix + '.' + str(i) if prefix else str(i)
                flatten_template(value, target, prefix=i_prefix)
        elif isinstance(struct, str):
            target[prefix] = struct

    pass1_template = resolve(template, kwargs)
    pass2_template = resolve(pass1_template, os.environ)
    local_vars = dict()
    flatten_template(pass2_template, local_vars)
    pass3_template = resolve(pass2_template, local_vars)
    return pass3_template


def dump_configuration(stream, template=None, **kwargs):
    initial_template = template if template else configuration_template()
    resolved_template = resolve_configuration_template(
        initial_template, **kwargs)
    yaml.dump(resolved_template, stream, default_flow_style=False)
