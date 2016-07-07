from jira import JIRA


class JiraClient:
    def __init__(self, jira_url, user=None, password=None):
        self.jira_url = jira_url
        self.user = user
        self.password = password
        self.jira = None

    def connect(self):
        auth = (self.user, self.password) if self.password else None
        self.jira = JIRA(self.jira_url, basic_auth=auth)
        return self.jira

    def iter_issues(self, jira_project, chunk_size=100, total=10000):
        query = 'project={0}'.format(jira_project)
        for chunk_i in range(1, total, chunk_size):
            chunk = self.jira.search_issues(query,
                                            startAt=chunk_i,
                                            maxResults=chunk_size,
                                            json_result=True)
            issues = chunk["issues"]
            if not issues:
                break
            for issue in issues:
                yield issue
