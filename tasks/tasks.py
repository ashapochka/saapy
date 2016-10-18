from invoke import task
from saapy import SecretStore, dump_configuration, Workspace
from saapy.clients import ScitoolsClient
from saapy.clients import Neo4jClient
from saapy.clients import GitClient
from saapy.etl import ScitoolsETL
from saapy.etl import GitETL
from saapy.antlr.tsql import print_tsql
from timeit import default_timer as timer
from datetime import timedelta, datetime
import os
import sys
import yaml
import getpass
import logging
import requests
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
from saapy.etl import build_neo4j_query


logging.basicConfig(style='{',
                    format='{asctime}:{levelname}:{name}:{message}',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
logging.getLogger('neo4j.bolt').setLevel(logging.WARNING)


@task
def hello(ctx):
    """
    checks invoke works
    :return: None
    """
    print("Hello!")
    logger.debug('debug message')
    logger.info('info message')
    logger.warn('warn message')
    logger.error('error message')
    logger.critical('critical message')


@task
def deps(ctx):
    """
    installs dependencies listed in requirements.txt with pip
    :return: None
    """
    ctx.run("pip install -U -r requirements.txt")


@task
def test(ctx):
    """
    runs tests for the library
    :return: None
    """
    ctx.run("py.test")


@task
def codecheck(ctx):
    """
    runs code quality checks using pep8 and other tools
    :return: None
    """
    ctx.run("py.test --pep8 -m pep8")


@task
def jupyter(ctx):
    """
    starts jupyter notebook server on the 8888++ port
    with its work directory in ./notebooks
    :param ctx:
    :return: None
    """
    ctx.run("jupyter-notebook --notebook-dir=notebooks")

@task
def gen_antlr_tsql(ctx):
    """
    generates python3 antlr parser code for T-SQL,
    depends on antlr4 installed and visible in the system
    :param ctx:
    :return: None
    """
    target_dir = "saapy/antlr/tsql/autogen"
    grammar_dir = "antlr/grammars-v4/tsql/tsql.g4"
    ctx.run("antlr4 -Dlanguage=Python3 -o {0} {1}".format(target_dir, grammar_dir))

# TODO: add tox configuration and link to travis-ci,
# ref http://docs.python-guide.org/en/latest/scenarios/ci/#tox


@task
def docker_neo4j_dump_config(ctx):
    ctx.run("docker run --rm --volume=$DOCKER_MOUNT_HOME/saapy/neo4j-assessment-graph/conf:/conf neo4j:latest dump-config")


# noinspection PyUnusedLocal
@task
def docker_build_base(ctx):
    ctx.run('docker build -f Dockerfile.base -t saapy-base .')


# noinspection PyUnusedLocal
@task
def docker_build(ctx):
    ctx.run('docker build -t saapy .')


# noinspection PyUnusedLocal
@task
def dcompose_refresh(ctx):
    ctx.run('docker-compose ps')
    ctx.run('docker-compose stop')
    ctx.run('docker-compose rm -f')
    ctx.run('docker-compose up -d')
    ctx.run('docker-compose ps')


# noinspection PyUnusedLocal
@task
def dcompose_restart(ctx):
    ctx.run('docker-compose ps')
    ctx.run('docker-compose stop')
    ctx.run('docker-compose up -d')
    ctx.run('docker-compose ps')


# noinspection PyUnusedLocal
@task
def dup(ctx):
    ctx.run('docker-compose up -d')
    ctx.run('docker-compose ps')


# noinspection PyUnusedLocal
@task
def dstop(ctx):
    ctx.run('docker-compose stop')
    ctx.run('docker-compose ps')


@task
def docker_cleanup(ctx):
    ctx.run('docker rm $(docker ps -q -f status=exited)')
    ctx.run('docker rmi -f $(docker images -q --filter "dangling=true")')


@task
def install_cfssl(ctx):
    ctx.run('go get -u github.com/cloudflare/cfssl/cmd/cfssl')
    ctx.run('go get -u github.com/cloudflare/cfssl/cmd/cfssljson')
    ctx.run('go get -u github.com/cloudflare/cfssl/cmd/mkbundle')

@task
def gen_root_cert(ctx):
    location = '$DOCKER_MOUNT_HOME/saapy/_shared/cert'
    ctx.run('cd {0} && cfssl gencert -initca \
    local.tdback.space-ca-csr.json | \
    cfssljson -bare local.tdback.space-ca -'.format(location))


@task
def gen_server_cert(ctx):
    location = '$DOCKER_MOUNT_HOME/saapy/_shared/cert'
    ctx.run('cd {0} && cfssl gencert \
    -ca=local.tdback.space-ca.pem \
    -ca-key=local.tdback.space-ca-key.pem \
    -config=local.tdback.space-ca-config.json \
    -profile=server \
    star.local.tdback.space-server.json | \
    cfssljson -bare star.local.tdback.space-server'.format(location))


@task
def gen_client_server_cert(ctx):
    location = '$DOCKER_MOUNT_HOME/saapy/_shared/cert'
    ctx.run('cd {0} && cfssl gencert \
    -ca=local.tdback.space-ca.pem \
    -ca-key=local.tdback.space-ca-key.pem \
    -config=local.tdback.space-ca-config.json \
    -profile=client-server \
    star.local.tdback.space-client-server.json | \
    cfssljson -bare star.local.tdback.space-client-server'.format(location))


@task
def gen_client_cert(ctx):
    location = '$DOCKER_MOUNT_HOME/saapy/_shared/cert'
    ctx.run('cd {0} && cfssl gencert \
    -ca=local.tdback.space-ca.pem \
    -ca-key=local.tdback.space-ca-key.pem \
    -config=local.tdback.space-ca-config.json \
    -profile=client \
    local.tdback.space-client.json | \
    cfssljson -bare local.tdback.space-client'.format(location))


@task
def verify_x509(ctx, certificate):
    ctx.run('openssl x509 -in {0} -text -noout'.format(certificate))


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
def export_scitools(ctx, udb_path, output_path):
    if os.path.exists(output_path):
        try:
            os.remove(output_path)
        except OSError as e:
            print("Error: %s - %s." % (e.filename, e.strerror))
    scitools_db = scitools_to_structs(udb_path)
    start = timer()
    with open(output_path, 'w') as output_stream:
        yaml.dump(scitools_db, output_stream)
    end = timer()
    execution_time = end - start
    print('transfer time:', timedelta(seconds=execution_time))


def scitools_to_structs(udb_path):
    scitools_client = ScitoolsClient(udb_path)
    scitools_client.connect()
    etl = ScitoolsETL(scitools_client.udb)
    scitools_db = dict()
    etl.transfer_to_struct_db(scitools_db)
    return scitools_db

# noinspection PyUnusedLocal
@task
def neo4j_password(ctx, user='neo4j'):
    password = getpass.getpass(prompt='Neo4j password for {0}: '.format(user))
    ctx['neo4j_password'] = password


# noinspection PyUnusedLocal
@task
def import_scitools_yaml_to_neo4j(ctx, yaml_path, neo4j_url='bolt://localhost',
                                  user='neo4j', labels=''):
    """

    :param labels:
    :param ctx:
    :param yaml_path:
    :param neo4j_url:
    :param user:
    """
    label_list = to_label_list(labels)
    with open(yaml_path, 'r') as input_stream:
        scitools_db = yaml.load(input_stream)
    neo4j_client = connect_neo4j(ctx, neo4j_url, user)
    ScitoolsETL.import_to_neo4j(scitools_db, neo4j_client, labels=label_list)


def connect_neo4j(ctx, neo4j_url, user):
    neo4j_password(ctx, user=user)
    neo4j_client = Neo4jClient(neo4j_url, user, ctx['neo4j_password'])
    neo4j_client.connect()
    return neo4j_client


# noinspection PyUnusedLocal
@task
def import_scitools_to_neo4j(ctx, udb_path, neo4j_url='bolt://localhost',
                                  user='neo4j', labels=''):
    """

    :param labels:
    :param ctx:
    :param yaml_path:
    :param neo4j_url:
    :param user:
    """
    label_list = to_label_list(labels)
    scitools_db = scitools_to_structs(udb_path)
    neo4j_client = connect_neo4j(ctx, neo4j_url, user)
    ScitoolsETL.import_to_neo4j(scitools_db, neo4j_client, labels=label_list)


def to_label_list(labels):
    label_list = labels.split(':') if labels else []
    return label_list


# noinspection PyUnusedLocal
@task
def import_git_to_neo4j(ctx, git_path, neo4j_url='bolt://localhost',
                        user='neo4j', labels=''):
    label_list = to_label_list(labels)
    neo4j_client = connect_neo4j(ctx, neo4j_url, user)
    git_client = GitClient(git_path)
    git_client.connect()
    etl = GitETL(git_client.repo)
    etl.import_to_neo4j(neo4j_client, labels=label_list)


# ns = Collection()
# ns.add_task(import_git_to_neo4j)

@task
def hello_future(ctx):
    from concurrent.futures import ThreadPoolExecutor
    from time import sleep
    import threading

    dummy_event = threading.Event()

    def long_task(exec_time):
        print('starting execution of {0}'.format(exec_time))
        # sleep(exec_time)
        dummy_event.wait(timeout=exec_time)
        return 'done {0}'.format(exec_time)

    with ThreadPoolExecutor(max_workers=2) as executor:
        future = executor.submit(long_task, 30)

        print('ok')
        dummy_event.set()
        print(future.result())


@task
def myip(ctx):
    """
    retrieves external ip address of the pc running this function
    by calling http://myexternalip.com
    :return: external ip address as a string
    """
    url = 'http://myexternalip.com/raw'
    r = requests.get(url)
    ext_ip = r.text.strip()
    print(ext_ip)


@task
def print_tsql(ctx, *tsql_paths):
    for path in tsql_paths:
        print_tsql(path)


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


@task
def commit_graph(ctx, workspace_configuration='conf/workspace.yml'):
    ws = Workspace(workspace_configuration)
    jpos = ws.project('jpos')
    neo = jpos.resource('neo4j_default')
    neo.connect()
    neo_client = neo.impl
    executor = ThreadPoolExecutor(max_workers=10)
    query = build_neo4j_query(neo_client, executor)
    q = query("""
MATCH (c:jpos:GitCommit)<--(ga:jpos:GitAuthor)<--(a:jpos:Actor)
WHERE SIZE(c.parents_hexsha) < 2 AND a.name <>"Travis"
WITH c, a
RETURN
c.authored_datetime AS commit_datetime,
a.name AS commit_author
ORDER BY c.authored_date
""")
    df = q.result()
    ts = pd.to_datetime(df['commit_datetime'].tolist())
    # del df['commit_datetime']
    df.index = ts
    commit_counts = df.commit_author.value_counts()
    top_commit_counts = commit_counts[commit_counts > commit_counts.quantile(0.9)]
    top_committers = top_commit_counts.index.tolist()
    top_df = df[df.commit_author.isin(top_committers)]
    print(top_df.ix['2015'])
    # ct = pd.crosstab(top_df.index, top_df.commit_author, margins=True)
    # print(ct.index)
    # ct.index = pd.to_datetime(ct.index)
    # print(ct[ct.index > datetime(2016, 1, 1)])
    # print(df.commit_author.unique())
    # df['commit_count'] = 1
    # del df['commit_date']
    # print(df)
    # del df['commit_datetime']
    # print(df.pivot('commit_datetime', 'commit_author', 'commit_count'))


@task
def run_apt_cacher(ctx):
    """
    see https://store.docker.com/community/images/sameersbn/apt-cacher-ng
    :param ctx:
    """
    ctx.run("""docker run --name apt-cacher-ng -d --restart=always \
    --publish 3142:3142 \
    --volume $DOCKER_MOUNT_HOME/apt-cacher-ng/cache:/var/cache/apt-cacher-ng \
    --volume $DOCKER_MOUNT_HOME/apt-cacher-ng/log:/var/log/apt-cacher-ng \
    sameersbn/apt-cacher-ng:latest
""")


@task
def run_devpi(ctx):
    """
    see https://store.docker.com/community/images/muccg/devpi
    :param ctx:
    """
    ctx.run("""docker run -d --name devpi \
    --publish 3141:3141 \
    --volume $DOCKER_MOUNT_HOME/devpi/data:/data \
    --restart always \
    dock-devpi
""")

@task
def run_jenkins_ca(ctx):
    """
    see https://store.docker.com/community/images/muccg/devpi
    :param ctx:
    """
    ctx.run("""docker run -d --name ca \
    --publish 8080:8080 --publish 50000:50000 \
    --volume $DOCKER_MOUNT_HOME/jenkins-ca/home:/var/jenkins_home \
    --restart always \
    jenkins-ca
""")

