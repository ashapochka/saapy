# coding=utf-8
import contextlib
import shelve
from collections import OrderedDict
from pathlib import Path
from pprint import pprint

import networkx as nx
import understand

import sys
from invoke import Program, task, Collection

from analysis import ActorSimilarityGraph
from saapy.analysis import ActorParser, csv_to_list
from saapy.vcs import GitClient


class Workspace:
    root_path: Path
    git_repo_path: Path
    analysis_dir_path: Path
    shelve_db_path: Path
    scitools_udb_path: Path

    def __init__(self, root_dir):
        self.root_path = Path(root_dir).resolve()
        self.git_repo_path = self.root_path / 'povray'
        self.analysis_dir_path = self.root_path / 'povray-analysis'
        self.shelve_db_path = self.analysis_dir_path / 'povray.shelve'
        self.scitools_udb_path = self.analysis_dir_path / 'povray-master1.udb'


def collect_source_files(git_graph):
    master_commit = git_graph.commit_node(ref_name='origin/master')['hexsha']
    return git_graph.collect_files(
        master_commit,
        tree_node='source',
        predicate=lambda f: f.endswith(('.cpp', '.h')))


def write_files_to_scitools_input_file(files, output_path, root_dir):
    with output_path.open('w') as out:
        for f in files:
            print(root_dir / f, file=out)


def build_similarity_graph(git_graph):
    actor_parser = ActorParser()
    role_names = csv_to_list(Path('../data/names.csv'))
    actor_parser.add_role_names(role_names)
    actors = [actor_parser.parse_actor(
        git_graph.commit_graph.node[actor_id]['name'],
        git_graph.commit_graph.node[actor_id]['email'])
        for actor_id in git_graph.actors]
    similarity_graph = ActorSimilarityGraph()
    for actor in actors:
        similarity_graph.add_actor(actor)
    return similarity_graph


def build_git_graph(git_repo_path, shelve_db_path):
    with shelve.open(str(shelve_db_path)) as db:
        if 'git_graph' in db:
            git_graph = db['git_graph']
        else:
            git_client = GitClient(git_repo_path)
            git_graph = git_client.build_commit_graph()
            git_client.add_commit_tree(git_graph, ref_name='origin/master')
            db['git_graph'] = git_graph
    return git_graph


def print_similarity_groups(similarity_graph):
    similar_groups = similarity_graph.group_similar_actors()
    for i, group in enumerate(similar_groups):
        if len(group) < 2:
            continue
        print('=== group', i, '===')
        for actor1_id, actor2_id, data \
                in similarity_graph.actor_graph.edges_iter(
            nbunch=group, data=True):
            print(actor1_id, '->', actor2_id, data)



@task
def cleanup(ctx):
    ws = Workspace(ctx.config.povray.parent_dir)
    with contextlib.suppress(FileNotFoundError):
        ws.shelve_db_path.unlink()
        ws.scitools_udb_path.unlink()


@task
def git_graph(ctx):
    ws = Workspace(ctx.config.povray.parent_dir)
    git_graph = build_git_graph(ws.git_repo_path, ws.shelve_db_path)
    print(len(git_graph.commit_graph))


@task
def sim_graph(ctx):
    ws = Workspace(ctx.config.povray.parent_dir)
    git_graph = build_git_graph(ws.git_repo_path, ws.shelve_db_path)
    similarity_graph = build_similarity_graph(git_graph)
    print_similarity_groups(similarity_graph)


@task
def understand(ctx):
    ws = Workspace(ctx.config.povray.parent_dir)
    git_graph = build_git_graph(ws.git_repo_path, ws.shelve_db_path)
    source_files = collect_source_files(git_graph)
    # pprint(git_graph.commit_graph.in_edges(nbunch=source_files))
    file_commits = OrderedDict()
    for f in source_files:
        file_commits[f] = git_graph.collect_commits(f)
    write_files_to_scitools_input_file(
        source_files, ws.analysis_dir_path / 'scitools-src.txt',
        ws.git_repo_path)
    scitools_udb = understand.open(str(ws.scitools_udb_path))
    for file_entity in scitools_udb.ents('file'):
        metric_names = file_entity.metrics()
        if len(metric_names):
            print(file_entity.longname())
            pprint(file_entity.metric(metric_names))


def main():
    program = Program(namespace=Collection.from_module(sys.modules[__name__]),
                      version='0.1.0')
    program.run()


if __name__ == '__main__':
    main()

