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
