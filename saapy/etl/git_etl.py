import time
import difflib
import pandas as pd
import logging


logger = logging.getLogger(__name__)


class GitETL:
    def __init__(self, repo):
        self.repo = repo

    @staticmethod
    def commit_to_struct(commit):
        stats = commit.stats
        parents = commit.parents
        commit_struct = dict(
            hexsha=commit.hexsha,
            author_name=commit.author.name,
            author_email=commit.author.email,
            authored_date=commit.authored_date,
            author_tz_offset=commit.author_tz_offset,
            authored_datetime=str(commit.authored_datetime),
            committer_name=commit.committer.name,
            committer_email=commit.committer.email,
            committed_date=commit.committed_date,
            committer_tz_offset=commit.committer_tz_offset,
            committed_datetime=str(commit.committed_datetime),
            summary=commit.summary,
            message=commit.message,
            encoding=commit.encoding,
            gpgsig=commit.gpgsig,
            parents_hexsha = [p.hexsha for p in parents],
            parent_hexsha=parents[0].hexsha if parents else None,
            name_rev=commit.name_rev,
            stats_total_lines = stats.total['lines'],
            stats_total_deletions = stats.total['deletions'],
            stats_total_files = stats.total['files'],
            stats_total_insertions = stats.total['insertions']
        )

        file_structs = []
        for file_name, file_stats in stats.files.items():
            file_struct = dict(file_stats)
            file_struct['file_name'] = file_name
            file_struct['commit_hexsha'] = commit_struct['hexsha']
            if commit_struct['parent_hexsha']:
                file_struct['parent_hexsha'] = commit_struct['parent_hexsha']
            file_structs.append(file_struct)

        return commit_struct, file_structs

    def export_revision_history(self):
        history = dict()
        commits = history['GitCommit'] = []
        file_stats = history['GitFileDiffStat'] = []
        visited_commit_hexsha = set()
        refs = self.repo.refs
        tips = history['GitRef'] = [dict(ref_name=ref.name,
                                         commit_hexsha=ref.commit.hexsha)
                                    for ref in refs]
        for tip in tips:
            ref_name, ref_commit_hexsha = tip['ref_name'], tip['commit_hexsha']
            logger.info('starting ref %s', ref_name)
            commit_count = 0
            for commit in self.repo.iter_commits(rev=ref_commit_hexsha):
                commit_hexsha = commit.hexsha
                if commit_hexsha in visited_commit_hexsha:
                    continue
                visited_commit_hexsha.add(commit_hexsha)
                commit_struct, file_structs = self.commit_to_struct(commit)
                if commit_hexsha == ref_commit_hexsha:
                    commit_struct['ref'] = ref_name
                commits.append(commit_struct)
                file_stats.extend(file_structs)
                commit_count += 1
            logger.info('commits processed: %s', commit_count)
        logger.info('history export complete')
        return history

    def import_to_neo4j(self, neo4j_client, labels=[]):
        history = self.export_revision_history()
        nodeset_names_to_import = history.keys()
        for nodeset_name in nodeset_names_to_import:
            node_labels = [nodeset_name] + labels
            nodes = history[nodeset_name]
            logger.info('importing %s nodes of %s', len(nodes), nodeset_name)
            neo4j_client.import_nodes(nodes, labels=node_labels)
            logger.info('%s imported', nodeset_name)

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
