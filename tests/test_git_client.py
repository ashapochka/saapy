# coding=utf-8
from pathlib import Path

import pytest
from git import Commit
from networkx.readwrite import json_graph

from saapy.util import dump_pretty_json
from saapy.vcs import GitClient
from vcs import check_file_move
from .test_utils import skip_on_travisciorg

repository_path = Path('..').resolve()
sample_revision = '4254c8c'
graph_json_path = Path('../data/saapy-graph.json')


def test_to_commit(data_root):
    git_client = GitClient(data_root / '../..')
    commit = git_client.to_commit(sample_revision)
    assert isinstance(commit, Commit)
    assert commit.hexsha.startswith(sample_revision)


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


