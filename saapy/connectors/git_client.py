from git import Repo


class GitClient:
    def __init__(self, local_repo_path):
        self.local_repo_path = local_repo_path
        self.repo = None

    def connect(self):
        self.repo = Repo(self.local_repo_path)
        return self.repo
