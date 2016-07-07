import itertools
import time
import difflib
import pandas as pd


class GitETL:
    def __init__(self, repo):
        self.repo = repo

    @staticmethod
    def commit_to_dict(c):
        d = dict(
            hexsha=c.hexsha,
            author_name=c.author.name,
            author_email=c.author.email,
            authored_date=c.authored_date,
            message=c.message,
            #         stats_lines = c.stats.total['lines'],
            #         stats_deletions = c.stats.total['deletions'],
            #         stats_files = c.stats.total['files'],
            #         stats_insertions = c.stats.total['insertions']
        )
        return d

    @staticmethod
    def commit_parents(c):
        for p in c.parents:
            d = dict(
                commit=c.hexsha,
                parent_commit=p.hexsha
            )
            yield d

    def export_commit_tree(self, commits_csv_path, parents_csv_path):
        commits = list(self.repo.iter_commits())
        commit_dicts = [self.commit_to_dict(c) for c in commits]
        cframe = pd.DataFrame(commit_dicts)
        cframe.to_csv(commits_csv_path, index=False)
        cparents = itertools.chain.from_iterable(
            (self.commit_parents(c) for c in commits))
        pframe = pd.DataFrame(list(cparents))
        pframe.to_csv(parents_csv_path, index=False)

    @staticmethod
    def lookup_refs_from_commits(commits_csv_path):
        # idempiere_jira_issue_id_pattern = re.compile(r"(
        # ?P<idempiere_jira_issue>IDEMPIERE-\d{1,4})")
        commits = pd.read_csv(commits_csv_path)
        messages = commits["message"]
        issues = messages.str.findall(
            r"(?P<idempiere_jira_issue>IDEMPIERE-\d{1,4})")
        commits['idempiere_jira_issues'] = issues
        return commits

    @staticmethod
    def print_commit(c):
        t = time.strftime("%a, %d %b %Y %H:%M", time.gmtime(c.authored_date))
        print(c.hexsha, c.author.name, t, c.message)
        print("stats:", c.stats.total)
        print()
        if len(c.parents):
            diffs = c.diff(c.parents[0])
            for d in diffs:
                print(d)
                b_lines = str(d.b_blob.data_stream.read()).split()
                a_lines = str(d.a_blob.data_stream.read()).split()
                differ = difflib.Differ()
                delta = differ.compare(b_lines, a_lines)
                for i in delta:
                    print(i)
                line_number = 0
                for line in delta:
                    # split off the code
                    code = line[:2]
                    # if the  line is in both files or just a, increment the
                    # line number.
                    if code in ("  ", "+ "):
                        line_number += 1
                    # if this line is only in a, print the line number and
                    # the text on the line
                    if code == "+ ":
                        print("%d: %s" % (line_number, line[2:].strip()))
                        # print(b_lines)
                        # print(a_lines)
                        #             dcont = list(difflib.unified_diff(
                        # b_lines, a_lines, d.b_path, d.a_path))
                        #             for l in dcont:
                        #                 print(l)
                print("------------------------")
        print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        print()
