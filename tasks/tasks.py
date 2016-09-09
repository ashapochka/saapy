from invoke import task, run


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
    run("pip install -U -r requirements.txt")


@task
def test(ctx):
    """
    runs tests for the library
    :return: None
    """
    run("py.test")


@task
def codecheck(ctx):
    """
    runs code quality checks using pep8 and other tools
    :return: None
    """
    run("py.test --pep8 -m pep8")


@task
def jupyter(ctx):
    """
    starts jupyter notebook server on the 8888++ port
    with its work directory in ./notebooks
    :param ctx:
    :return: None
    """
    run("jupyter-notebook --notebook-dir=notebooks")

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
    run("antlr4 -Dlanguage=Python3 -o {0} {1}".format(target_dir, grammar_dir))

# TODO: add tox configuration and link to travis-ci,
# ref http://docs.python-guide.org/en/latest/scenarios/ci/#tox


@task
def docker_neo4j_dump_config(ctx):
    run("docker run --rm --volume=$DOCKER_MOUNT_HOME/saapy/neo4j-assessment-graph/conf:/conf neo4j:latest dump-config")


# noinspection PyUnusedLocal
@task
def docker_build_base(context):
    run('docker build -f Dockerfile.base -t saapy-base .')


# noinspection PyUnusedLocal
@task
def dcompose_refresh(context):
    run('docker-compose ps')
    run('docker-compose stop')
    run('docker-compose rm -f')
    run('docker-compose up -d')


@task
def docker_cleanup(context):
    run('docker rm $(docker ps -q -f status=exited)')
    run('docker rmi -f $(docker images -q --filter "dangling=true")')


@task
def gen_root_cert(context):
    location = '$DOCKER_MOUNT_HOME/saapy/_shared/cert'
    run('cd {0} && cfssl gencert -initca \
    local.tdback.space-ca-csr.json | \
    cfssljson -bare local.tdback.space-ca -'.format(location))


@task
def gen_server_cert(context):
    location = '$DOCKER_MOUNT_HOME/saapy/_shared/cert'
    run('cd {0} && cfssl gencert \
    -ca=local.tdback.space-ca.pem \
    -ca-key=local.tdback.space-ca-key.pem \
    -config=local.tdback.space-ca-config.json \
    -profile=server \
    star.local.tdback.space-server.json | \
    cfssljson -bare star.local.tdback.space-server'.format(location))


@task
def gen_client_server_cert(context):
    location = '$DOCKER_MOUNT_HOME/saapy/_shared/cert'
    run('cd {0} && cfssl gencert \
    -ca=local.tdback.space-ca.pem \
    -ca-key=local.tdback.space-ca-key.pem \
    -config=local.tdback.space-ca-config.json \
    -profile=client-server \
    star.local.tdback.space-client-server.json | \
    cfssljson -bare star.local.tdback.space-client-server'.format(location))


@task
def gen_client_cert(context):
    location = '$DOCKER_MOUNT_HOME/saapy/_shared/cert'
    run('cd {0} && cfssl gencert \
    -ca=local.tdback.space-ca.pem \
    -ca-key=local.tdback.space-ca-key.pem \
    -config=local.tdback.space-ca-config.json \
    -profile=client \
    local.tdback.space-client.json | \
    cfssljson -bare local.tdback.space-client'.format(location))


@task
def verify_x509(ctx, certificate):
    ctx.run('openssl x509 -in {0} -text -noout'.format(certificate))
