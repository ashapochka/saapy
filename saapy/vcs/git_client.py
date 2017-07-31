# coding=utf-8

"""
the module implements git client extracting project history from the local
repository
"""
import logging

from git import Repo, Commit

from .git_commit_utils import commit_history_to_frames

logger = logging.getLogger(__name__)


class GitClient:
    """
    connects to the local git repository and extracts project history
    """

    def __init__(self, local_repo_path):
        self.local_repo_path = local_repo_path
        self.repository = Repo(str(self.local_repo_path))

    def to_commit(self, revision) -> Commit:
        if isinstance(revision, str) or revision is None:
            commit = self.repository.commit(rev=revision)
        elif isinstance(revision, Commit):
            commit = revision
        else:
            commit = None
        return commit

    def extract_commit_history(self,
                               revs='all_refs',
                               include_trees=True,
                               paths='',
                               **kwargs) -> dict:
        return commit_history_to_frames(self.repository,
                                        revs=revs,
                                        include_trees=include_trees,
                                        paths=paths,
                                        **kwargs)
