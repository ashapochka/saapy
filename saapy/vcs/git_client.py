# coding=utf-8

"""
the module implements git client extracting project history from the local
repository
"""
import difflib
import logging
import re

import time
from collections import namedtuple

import networkx as nx
from git import Repo, Commit, Reference, TagReference, Tree
from recordclass import recordclass

logger = logging.getLogger(__name__)


GitHistory = namedtuple('GitHistory',
                        ['GitCommit', 'GitFileDiffStat', 'GitRef'])


FileCommit = recordclass('FileCommit', ['commit', 'lines', 'when'])


class GitGraph:
    commit_graph = None
    ref_commits = None
    tag_commits = None
    actors = None
    commit_trees = None

    def __init__(self):
        self.commit_graph = nx.DiGraph()
        self.ref_commits = set()
        self.tag_commits = set()
        self.actors = set()
        self.commit_trees = dict()

    def filter_by_attr(self, node_labels, **kwargs):
        def predicate(hexsha):
            n = self.commit_node(hexsha=hexsha)
            eq = lambda key: n[key] != kwargs[key]
            return next(filter(eq, kwargs.keys()), None) is None
        return filter(predicate, node_labels)

    def commit_node(self, hexsha=None, ref_name=None, tag_name=None):
        if hexsha:
            commit_hexsha = hexsha
        elif ref_name:
            commit_hexsha = next(self.filter_by_attr(self.ref_commits,
                                                     ref_name=ref_name), None)
        elif tag_name:
            commit_hexsha = next(self.filter_by_attr(self.tag_commits,
                                                     tag_name=tag_name), None)
        if commit_hexsha:
            return self.commit_graph.node[commit_hexsha]
        else:
            return None

    def add_ref(self, ref: Reference):
        self.commit_graph.add_node(ref.commit.hexsha,
                                   ref_name=ref.name,
                                   ref_head=True)
        self.ref_commits.add(ref.commit.hexsha)

    def add_tag(self, tag: TagReference):
        self.commit_graph.add_node(tag.commit.hexsha,
                                   tag_name=tag.name,
                                   tag_head=True)
        self.tag_commits.add(tag.commit.hexsha)

    def add_actor(self, actor):
        name = actor.name
        email = actor.email
        node_label = '{} <{}>'.format(name, email)
        self.actors.add(node_label)
        self.commit_graph.add_node(node_label,
                                   name=name,
                                   email=email,
                                   node_type='actor')
        return node_label

    def add_commit(self, commit: Commit):
        hexsha = commit.hexsha
        stats = commit.stats
        parents = commit.parents
        commit_attrs = dict(
            hexsha=hexsha,
            authored_date=commit.authored_date,
            author_tz_offset=commit.author_tz_offset,
            authored_datetime=commit.authored_datetime.isoformat(),
            committed_date=commit.committed_date,
            committer_tz_offset=commit.committer_tz_offset,
            committed_datetime=commit.committed_datetime.isoformat(),
            summary=commit.summary,
            message=commit.message,
            encoding=commit.encoding,
            gpgsig=commit.gpgsig,
            name_rev=commit.name_rev,
            stats_total_lines=stats.total['lines'],
            stats_total_deletions=stats.total['deletions'],
            stats_total_files=stats.total['files'],
            stats_total_insertions=stats.total['insertions'],
            node_type='commit',
            parent_count=len(parents)
        )
        self.commit_graph.add_node(commit.hexsha, attr_dict=commit_attrs)
        author_label = self.add_actor(commit.author)
        self.commit_graph.add_edge(author_label, hexsha, author=True,
                                   edge_type='commit_actor')
        committer_label = self.add_actor(commit.committer)
        self.commit_graph.add_edge(committer_label, hexsha, committer=True,
                                   edge_type='commit_actor')
        self.commit_graph.add_edges_from([(hexsha, p.hexsha) for p in parents],
                                         edge_type='parent')
        for file_name, file_stats in stats.files.items():
            old_file_path, new_file_path = check_file_move(file_name)
            self.commit_graph.add_node(old_file_path,
                                       path=old_file_path,
                                       node_type='file')
            file_attrs = dict(file_stats)
            file_attrs['path'] = file_name
            if old_file_path == new_file_path:
                file_attrs['operation'] = 'edit'
            else:
                file_attrs['operation'] = 'move'
                self.commit_graph.add_node(new_file_path,
                                           path=new_file_path,
                                           node_type='file')
                self.commit_graph.add_edge(old_file_path,
                                           new_file_path,
                                           edge_type='file_move')
            self.commit_graph.add_edge(hexsha,
                                       old_file_path,
                                       attr_dict=file_attrs,
                                       edge_type='included_file')

    def add_commit_tree(self, commit: Commit):
        self.commit_trees[commit.hexsha] = commit_tree = nx.DiGraph()
        self._add_tree(commit_tree, commit.tree)
        return commit.hexsha

    def _add_tree(self, commit_tree: nx.DiGraph, tree: Tree,
                  empty_replacement='.'):
        tree_node_id = tree.path or empty_replacement
        commit_tree.add_node(tree_node_id, path=tree.path, node_type='tree')
        for blob in tree.blobs:
            commit_tree.add_node(blob.path,
                                 path=blob.path,
                                 node_type='file')
            commit_tree.add_edge(tree_node_id, blob.path,
                                 edge_type='tree')
        for subtree in tree.trees:
            subtree_node_id = self._add_tree(commit_tree, subtree)
            commit_tree.add_edge(tree_node_id, subtree_node_id,
                                 edge_type='tree')
        return tree_node_id

    def collect_commits(self, file_node):
        commits = []
        for predecessor in self.commit_graph.predecessors(file_node):
            pred_node = self.commit_graph.node[predecessor]
            predecessor_type = pred_node['node_type']
            if predecessor_type == 'commit':
                if pred_node['parent_count'] > 1:
                    pass
                else:
                    commits.append(FileCommit(
                        commit=predecessor,
                        lines=self.commit_graph[predecessor][file_node]['lines'],
                        when=pred_node['authored_datetime']))
            elif predecessor_type == 'file':
                commits.extend(self.collect_commits(predecessor))
            else:
                pass
        return commits

    def collect_files(self, commit, tree_node='.', predicate=lambda f: True):
        commit_tree = self.commit_trees[commit]
        tree_edges = list(nx.bfs_edges(commit_tree, tree_node))
        files = [edge[1] for edge in tree_edges
                 if (commit_tree.node[edge[1]]['node_type'] == 'file'
                     and predicate(edge[1]))]
        return files


class GitClient:
    """
    connects to the local git repository and extracts project history
    """

    def __init__(self, local_repo_path):
        self.local_repo_path = local_repo_path
        self.repository = Repo(self.local_repo_path)

    def commit_to_struct(self, revision):
        commit = self.to_commit(revision)
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
            parents_hexsha=[p.hexsha for p in parents],
            parent_hexsha=parents[0].hexsha if parents else None,
            name_rev=commit.name_rev,
            stats_total_lines=stats.total['lines'],
            stats_total_deletions=stats.total['deletions'],
            stats_total_files=stats.total['files'],
            stats_total_insertions=stats.total['insertions']
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

    def to_commit(self, revision):
        if isinstance(revision, str) or revision is None:
            commit = self.repository.commit(rev=revision)
        elif isinstance(revision, Commit):
            commit = revision
        return commit

    def build_commit_graph(self):
        graph = GitGraph()
        visited_commit_hexsha = set()
        refs = self.repository.refs
        for ref in refs:
            ref_name, ref_commit_hexsha = ref.name, ref.commit.hexsha
            logger.info('starting ref %s', ref_name)
            commit_count = 0
            graph.add_ref(ref)
            for commit in self.repository.iter_commits(rev=ref_commit_hexsha):
                commit_hexsha = commit.hexsha
                if commit_hexsha in visited_commit_hexsha:
                    continue
                else:
                    visited_commit_hexsha.add(commit_hexsha)
                graph.add_commit(commit)
                commit_count += 1
            logger.info('commits processed: %s', commit_count)
        tags = self.repository.tags
        for tag in tags:
            graph.add_tag(tag)
        logger.info('history export complete')
        return graph

    def add_commit_tree(self, graph: GitGraph,
                        hexsha=None, ref_name=None, tag_name=None):
        commit_node = graph.commit_node(hexsha=hexsha,
                                        ref_name=ref_name,
                                        tag_name=tag_name)
        graph.add_commit_tree(self.to_commit(commit_node['hexsha']))
        return commit_node['hexsha']

    def revision_history(self):
        history = GitHistory()
        commits = history.GitCommit = []
        file_stats = history.GitFileDiffStat = []
        visited_commit_hexsha = set()
        refs = self.repository.refs
        tips = history.GitRef = [dict(ref_name=ref.name,
                                         commit_hexsha=ref.commit.hexsha)
                                    for ref in refs]
        for tip in tips:
            ref_name, ref_commit_hexsha = tip['ref_name'], tip['commit_hexsha']
            logger.info('starting ref %s', ref_name)
            commit_count = 0
            for commit in self.repository.iter_commits(rev=ref_commit_hexsha):
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
        history = self.revision_history()
        nodeset_names_to_import = history.keys()
        for nodeset_name in nodeset_names_to_import:
            node_labels = [nodeset_name] + labels
            nodes = history[nodeset_name]
            logger.info('importing %s nodes of %s', len(nodes), nodeset_name)
            neo4j_client.import_nodes(nodes, labels=node_labels)
            logger.info('%s imported', nodeset_name)

    def print_commit(self, revision, with_diff=False):
        c = self.to_commit(revision)
        t = time.strftime("%a, %d %b %Y %H:%M", time.gmtime(c.authored_date))
        print(c.hexsha, c.author.name, t, c.message)
        print("stats:", c.stats.total)
        print()
        if with_diff and len(c.parents):
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


def check_file_move(file_path):
    m = re.match(r'(.*)(\{.*\s\=\>\s.*\})(.*)', file_path)
    try:
        pre_part = m.group(1)
        change_part = m.group(2)
        post_part = m.group(3)
    except:
        pre_part = ''
        change_part = file_path
        post_part = ''
    m = re.match(r'[\{]?(.*)\s\=\>\s([^\}]*)[\}]?', change_part)
    try:
        old_part = m.group(1)
        new_part = m.group(2)
        old_file_name = combine_path_parts(pre_part, old_part, post_part)
        new_file_name = combine_path_parts(pre_part, new_part, post_part)
        return old_file_name, new_file_name
    except:
        return change_part, change_part


def combine_path_parts(pre_part, inner_part, post_part):
    if inner_part:
        file_path = pre_part + inner_part + post_part
    elif pre_part.endswith('/') and post_part.startswith('/'):
        file_path = pre_part[:-1] + post_part
    else:
        file_path = pre_part + post_part
    return file_path
