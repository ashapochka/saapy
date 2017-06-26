# coding=utf-8
from pathlib import Path

from git import Commit
from networkx.readwrite import json_graph

from saapy.analysis import dump_pretty_json
from saapy.vcs import GitClient
from vcs.git_client import check_file_move

repository_path = Path('..').resolve()
sample_revision = '4254c8c'
graph_json_path = Path('../data/saapy-graph.json')


def test_to_commit():
    git_client = GitClient(repository_path)
    commit = git_client.to_commit(sample_revision)
    assert isinstance(commit, Commit)
    assert commit.hexsha.startswith(sample_revision)


def test_build_commit_graph():
    git_client = GitClient(repository_path)
    graph = git_client.build_commit_graph()
    git_client.add_commit_tree(graph, ref_name='origin/master')
    dump_pretty_json(json_graph.node_link_data(graph.commit_graph),
                     graph_json_path)


def test_file_move_parsing():
    print()
    samples = ['tests/{ => data/ws1}/conf/workspace.yaml',
               'saapy/{scitools.py => clients/scitools_client.py}',
               '{saapy/scripts => scripts}/manage_password.py',
               'Dockerfile => dock/Dockerfile',
               'saapy/{antlr => lang}/__init__.py',
               'tasks/__init__.py']
    for i, sample in enumerate(samples):
        old_file_path, new_file_path = check_file_move(sample)
        if i < len(samples) - 1:
            assert old_file_path != new_file_path
        else:
            assert old_file_path == new_file_path


