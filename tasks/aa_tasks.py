# coding=utf-8
import logging
import os
from datetime import timedelta
from timeit import default_timer as timer

import yaml
from invoke import task

import saapy.analysis
from .admin_tasks import connect_neo4j
from saapy.codetools import ScitoolsClient
from saapy.codetools import ScitoolsETL
from saapy.lang.tsql import print_tsql
from saapy.vcs import GitClient
from saapy.vcs import GitETL

# from saapy.etl import build_neo4j_query


logging.basicConfig(style='{',
                    format='{asctime}:{levelname}:{name}:{message}',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
logging.getLogger('neo4j.bolt').setLevel(logging.WARNING)


@task
def notebook(ctx):
    """
    starts jupyter notebook server on the 8888++ port
    with its work directory in ./samples
    :param ctx:
    :return: None
    """
    ctx.run("jupyter-notebook --notebook-dir=samples")


@task
def gen_antlr_tsql(ctx):
    """
    generates python3 lang parser code for T-SQL,
    depends on antlr4 installed and visible in the system
    :param ctx:
    :return: None
    """
    target_dir = "saapy/lang/tsql/autogen"
    grammar_dir = "antlr/grammars-v4/tsql/tsql.g4"
    ctx.run("antlr4 -Dlanguage=Python3 -o {0} {1}".format(target_dir, grammar_dir))


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
    scitools_client.open_udb()
    etl = ScitoolsETL(scitools_client.udb)
    scitools_db = dict()
    etl.transfer_to_struct_db(scitools_db)
    return scitools_db


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


@task
def print_tsql(ctx, *tsql_paths):
    for path in tsql_paths:
        print_tsql(path)


# @task
# def commit_graph(ctx, workspace_configuration='conf/workspace.yml'):
#     ws = Workspace(workspace_configuration)
#     jpos = ws.project('jpos')
#     neo = jpos.resource('neo4j_default')
#     neo.connect()
#     neo_client = neo.impl
#     executor = ThreadPoolExecutor(max_workers=10)
#     query = build_neo4j_query(neo_client, executor)
#     q = query("""
# MATCH (c:jpos:GitCommit)<--(ga:jpos:GitAuthor)<--(a:jpos:Actor)
# WHERE SIZE(c.parents_hexsha) < 2 AND a.name <>"Travis"
# WITH c, a
# RETURN
# c.authored_datetime AS commit_datetime,
# a.name AS commit_author
# ORDER BY c.authored_date
# """)
#     df = q.result()
#     ts = pd.to_datetime(df['commit_datetime'].tolist())
#     # del df['commit_datetime']
#     df.index = ts
#     commit_counts = df.commit_author.value_counts()
#     top_commit_counts = commit_counts[commit_counts > commit_counts.quantile(0.9)]
#     top_committers = top_commit_counts.index.tolist()
#     top_df = df[df.commit_author.isin(top_committers)]
#     print(top_df.ix['2015'])
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
def grep(ctx, file_pattern, search_pattern):
    for result in saapy.analysis.regrep(file_pattern, search_pattern):
        print(result)
