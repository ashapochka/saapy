from invoke import task, run


@task
def hello():
    """
    checks invoke works
    :return: None
    """
    print("Hello!")


@task
def deps():
    """
    installs dependencies listed in requirements.txt with pip
    :return: None
    """
    run("pip install -U -r requirements.txt")


@task
def test():
    """
    runs tests for the library
    :return: None
    """
    run("py.test")


@task
def codecheck():
    """
    runs code quality checks using pep8 and other tools
    :return: None
    """
    run("py.test --pep8 -m pep8")

# TODO: add tox configuration and link to travis-ci,
# ref http://docs.python-guide.org/en/latest/scenarios/ci/#tox
