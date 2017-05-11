import json


class JiraETL:
    def __init__(self, jira):
        self.jira = jira

    def export_jira_issues(self, project_name, issues_json_file):
        issues = list(self.jira.iter_issues(project_name))
        s = json.dumps(issues, indent=4)
        issues_json_file.write_text(s)
