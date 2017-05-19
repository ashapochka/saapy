# coding=utf-8
import getpass

import sys
import yaml
from invoke import task

from saapy.graphdb import Neo4jClient
from saapy import Workspace, SecretStore, dump_configuration


@task
def encrypt_secrets(ctx, plain_store_yaml_path, key_yaml_path=None,
                    store_yaml_path=None):
    secret_store = SecretStore.load_from_yaml(key_yaml_path, plain_store_yaml_path,
                                              encrypted=False)
    secret_store.save_as_yaml(store_yaml_path)


@task
def gen_master_key(ctx, key_yaml_path):
    SecretStore.add_master_key(key_yaml_path)


@task
def set_secret(ctx, secret, service=None, user=None, key_yaml_path=None,
               store_yaml_path=None):
    secret_store = SecretStore.load_from_yaml(key_yaml_path, store_yaml_path,
                                              encrypted=True)
    path = []
    path = path + [service] if service else path
    path = path + [user] if user else path
    secret_store.set_secret(secret, *path)
    secret_store.save_as_yaml(store_yaml_path)


@task
def set_ws_secret(ctx, conf_path=None, resource=None):
    ws = Workspace(conf_path)
    user_name = ws.get_resource_user(resource)
    secret = getpass.getpass(
        prompt="User {0} password for resource {1}: ".format(
            user_name, resource))
    ws.secret_store.set_secret(secret, resource, user_name)
    ws.save_configuration()


# noinspection PyUnusedLocal
@task
def neo4j_password(ctx, user='graphdb'):
    password = getpass.getpass(prompt='Neo4j password for {0}: '.format(user))
    ctx['neo4j_password'] = password


def connect_neo4j(ctx, neo4j_url, user):
    neo4j_password(ctx, user=user)
    neo4j_client = Neo4jClient(neo4j_url, user, ctx['neo4j_password'])
    neo4j_client.connect()
    return neo4j_client


@task
def dump_conf(ctx, output=None, template_path=None):
    if template_path:
        with open(template_path, 'r') as template_yaml_file:
            template = yaml.load(template_yaml_file)
    else:
        template = None
    if output:
        with open(output, 'w') as yaml_file:
            dump_configuration(yaml_file, template=template)
    else:
        dump_configuration(sys.stdout, template=template)


@task
def tpl(ctx):
    from string import Template
    class Tpl(Template):
        idpattern = r'[_a-z][\._a-z0-9]*'

    t = Tpl('${workspace.work_directory}/conf/secret.yml')
    s = t.safe_substitute(
        {'workspace.work_directory': '/Users/ashapoch/Dropbox/_projects/saapy'})
    print(s)
