# coding=utf-8
import shelve
from collections import OrderedDict
from pathlib import Path
from pprint import pprint

import networkx as nx

from analysis import ActorSimilarityGraph
from saapy.analysis import ActorParser, csv_to_list
from saapy.vcs import GitClient


def main():
    root_path = Path('../../../3party')
    git_repo_path = root_path / 'povray'
    analysis_dir_path = root_path / 'povray-analysis'
    shelve_db_path = analysis_dir_path / 'povray.shelve'
    git_graph = build_git_graph(git_repo_path, shelve_db_path)
    similarity_graph = build_similarity_graph(git_graph)
    # print_similarity_groups(similarity_graph)
    master_commit = git_graph.commit_node(ref_name='origin/master')['hexsha']
    master_tree = git_graph.commit_trees[master_commit]
    source_tree_edges = list(nx.bfs_edges(master_tree, 'source'))
    source_files = [edge[1] for edge in source_tree_edges
                    if master_tree.node[edge[1]]['node_type'] == 'file']
    source_files = [f for f in source_files
                    if f.endswith('.cpp') or f.endswith('.h')]
    # pprint(git_graph.commit_graph.in_edges(nbunch=source_files))
    file_commits = OrderedDict()
    for f in source_files:
        file_commits[f] = collect_commits(git_graph.commit_graph, f)
    pprint(file_commits)
    # pprint(git_graph.commit_graph['4f39fd014b6c8806699f157b6700646f39539fac'])
    # pprint(git_graph.commit_graph.in_edges('source/backend/frame.h'))



def collect_commits(commit_graph: nx.DiGraph, file_node):
    commits = []
    for predecessor in commit_graph.predecessors(file_node):
        predecessor_type = commit_graph.node[predecessor]['node_type']
        if predecessor_type == 'commit':
            if commit_graph.node[predecessor]['parent_count'] > 1:
                pass
            else:
                commits.append(predecessor)
        elif predecessor_type == 'file':
            commits.extend(collect_commits(commit_graph, predecessor))
        else:
            pass
    return commits


def build_similarity_graph(git_graph):
    actor_parser = ActorParser()
    role_names = csv_to_list(Path('../data/names.csv'))
    actor_parser.add_role_names(role_names)
    actors = [actor_parser.parse_actor(
        git_graph.commit_graph.node[actor_id]['name'],
        git_graph.commit_graph.node[actor_id]['email'])
        for actor_id in git_graph.actors]
    similarity_graph = ActorSimilarityGraph()
    for actor in actors:
        similarity_graph.add_actor(actor)
    return similarity_graph


def build_git_graph(git_repo_path, shelve_db_path):
    with shelve.open(str(shelve_db_path)) as db:
        if 'git_graph' in db:
            git_graph = db['git_graph']
        else:
            git_client = GitClient(git_repo_path)
            git_graph = git_client.build_commit_graph()
            git_client.add_commit_tree(git_graph, ref_name='origin/master')
            db['git_graph'] = git_graph
    return git_graph


def print_similarity_groups(similarity_graph):
    similar_groups = similarity_graph.group_similar_actors()
    for i, group in enumerate(similar_groups):
        if len(group) < 2:
            continue
        print('=== group', i, '===')
        for actor1_id, actor2_id, data \
                in similarity_graph.actor_graph.edges_iter(
            nbunch=group, data=True):
            print(actor1_id, '->', actor2_id, data)


if __name__ == '__main__':
    main()
