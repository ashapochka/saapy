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

# TODO: add tox configuration and link to travis-ci,
# ref http://docs.python-guide.org/en/latest/scenarios/ci/#tox
