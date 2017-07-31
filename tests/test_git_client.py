# coding=utf-8

from git import Commit

from saapy.vcs import GitClient, check_file_move


sample_revision = '4254c8c'


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
