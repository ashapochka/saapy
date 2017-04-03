from invoke import task
import contextlib
import os
from pathlib import Path


@contextlib.contextmanager
def directory(dirname=None):
    """
    changes current directory to dirname
    used as with directory(dirname) as dir to
    move out of the changed directory at the end
    :param dirname: directory to change into
    """
    curdir = os.getcwd()
    try:
        if dirname is not None:
            os.chdir(dirname)
        yield Path(dirname or curdir)
    finally:
        os.chdir(curdir)


def build_image(ctx, image_name, tag):
    with directory('dock/{}'.format(image_name)):
        ctx.run('docker build -t saapy/{0}:{1} .'.format(image_name, tag))


@task
def build_assessment_notebook(ctx, tag='latest'):
    build_image(ctx, "assessment-notebook", tag)


@task
def build_graph_database(ctx, tag='latest'):
    build_image(ctx, "graph-database", tag)
    
    
@task(
    build_assessment_notebook,
    build_graph_database)
def build_all_images(ctx):
    pass


@task
def cleanup_images(ctx):
    ctx.run('docker rmi -f $(docker images -q --filter "dangling=true")')


@task
def cleanup_containers(ctx):
    ctx.run('docker rm $(docker ps -q -f status=exited)')


@task(
    cleanup_containers,
    cleanup_images)
def cleanup_all(ctx):
    pass


@task
def stop_system(ctx):
    with directory('assessment-system'):
        ctx.run('docker-compose stop')
        ctx.run('docker-compose ps')


@task
def start_system(ctx):
    with directory('assessment-system'):
        ctx.run('docker-compose up -d')
        ctx.run('docker-compose ps')


@task(stop_system, start_system)
def restart_system(ctx):
    pass


@task(stop_system)
def drop_system(ctx):
    with directory('assessment-system'):
        ctx.run('docker-compose rm -f')


@task(drop_system, start_system)
def reset_system(ctx):
    pass


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
def docker_neo4j_dump_config(ctx):
    ctx.run("docker run --rm --volume=$DOCKER_MOUNT_HOME/saapy/neo4j-assessment-graph/conf:/conf neo4j:latest dump-config")


@task
def run_apt_cacher(ctx):
    """
    see https://encrypted_store.docker.com/community/images/sameersbn/apt-cacher-ng
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
    see https://encrypted_store.docker.com/community/images/muccg/devpi
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
    see https://encrypted_store.docker.com/community/images/muccg/devpi
    :param ctx:
    """
    ctx.run("""docker run -d --name ca \
    --publish 8080:8080 --publish 50000:50000 \
    --volume $DOCKER_MOUNT_HOME/jenkins-ca/home:/var/jenkins_home \
    --restart always \
    jenkins-ca
""")
