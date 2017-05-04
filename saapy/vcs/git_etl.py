import time
import difflib
import pandas as pd
import logging


logger = logging.getLogger(__name__)


class GitETL:
    def __init__(self, repo):
        self.repo = repo



    @staticmethod
    def lookup_refs_from_commits(commits_csv_path):
        # idempiere_jira_issue_id_pattern = re.compile(r"(
        # ?P<idempiere_jira_issue>IDEMPIERE-\d{1,4})")
        commits = pd.read_csv(commits_csv_path)
        messages = commits["message"]
        issues = messages.str.findall(
            r"(?P<idempiere_jira_issue>IDEMPIERE-\d{1,4})")
        commits['idempiere_jira_issues'] = issues
        commits[commits['idempiere_jira_issues'].apply(
            lambda issues: (type(issues) == list and len(issues) > 0))]
        return commits


