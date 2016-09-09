from invoke import task
from saapy import SecretStore
from saapy.clients import ScitoolsClient
from saapy.clients import Neo4jClient
from saapy.etl import ScitoolsETL
from timeit import default_timer as timer
from datetime import timedelta
import os
import yaml
import getpass


@task
def hello(ctx):
    """
    checks invoke works
    :return: None
    """
    print("Hello!")


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
    secret_store = SecretStore.from_yaml(key_yaml_path, plain_store_yaml_path,
                                         encrypted=False)
    secret_store.save_as_yaml(store_yaml_path)


@task
def gen_master_key(ctx, key_yaml_path):
    SecretStore.add_master_key(key_yaml_path)


@task
def set_secret(ctx, secret, service=None, user=None, key_yaml_path=None,
               store_yaml_path=None):
    secret_store = SecretStore.from_yaml(key_yaml_path, store_yaml_path,
                                         encrypted=True)
    path = []
    path = path + [service] if service else path
    path = path + [user] if user else path
    secret_store.set_secret(secret, *path)
    secret_store.save_as_yaml(store_yaml_path)


# noinspection PyUnusedLocal
@task
def export_scitools(ctx, udb_path, output_path):
    if os.path.exists(output_path):
        try:
            os.remove(output_path)
        except OSError as e:
            print("Error: %s - %s." % (e.filename, e.strerror))
    scitools_client = ScitoolsClient(udb_path)
    scitools_client.connect()
    etl = ScitoolsETL(scitools_client.udb)
    scitools_db = dict()
    start = timer()
    etl.transfer_to_struct_db(scitools_db)
    with open(output_path, 'w') as output_stream:
        yaml.dump(scitools_db, output_stream)
    end = timer()
    execution_time = end - start
    print('transfer time:', timedelta(seconds=execution_time))


# noinspection PyUnusedLocal
@task
def import_scitools_yaml_to_neo4j(ctx, yaml_path, neo4j_url, user='neo4j'):
    """

    :param ctx:
    :param yaml_path:
    :param neo4j_url:
    :param user:
    """
    with open(yaml_path, 'r') as input_stream:
        scitools_db = yaml.load(input_stream)
    password = getpass.getpass(prompt='Neo4j password for {0}: '.format(user))
    neo4j_client = Neo4jClient(neo4j_url, user, password)
    neo4j_client.connect()
    ScitoolsETL.import_to_neo4j(scitools_db, neo4j_client)
