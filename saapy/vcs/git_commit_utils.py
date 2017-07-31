# coding=utf-8
import re

import networkx as nx
import pandas as pd

import saapy.util as su


def commit_history_to_frames(repo, revs='all_refs',
                             include_trees=True,
                             paths='', **kwargs):
    ref_frame = refs_to_ref_frame(repo.refs)
    if revs == 'all_refs':
        commit_revs = (ref.commit.hexsha for ref in repo.refs)
    else:
        commit_revs = revs
    commits = get_commits(repo, commit_revs, paths=paths, **kwargs)
    actor_frame = commits_to_actor_frame(commits)
    commit_frame = commits_to_frame(commits)
    stats_files_frame = commit_frame[['hexsha', 'stats_files']]
    commit_frame.drop('stats_files', axis=1, inplace=True)
    file_frame = stats_files_to_frame(stats_files_frame)
    parent_frame = commit_parents_to_frame(commits)
    result = dict(ref_frame=ref_frame,
                  actor_frame=actor_frame,
                  commit_frame=commit_frame,
                  file_frame=file_frame,
                  parent_frame=parent_frame)
    if include_trees:
        tree_frame = commit_trees_to_frame(commits)
        result['tree_frame'] = tree_frame
    return result


def stats_files_to_frame(stats_files_frame):
    file_changes = []
    for row in stats_files_frame.itertuples():
        for file_path, file_change in row.stats_files.items():
            file_path1, file_path2 = check_file_move(file_path)
            move = file_path1 != file_path2
            d = dict(hexsha=row.hexsha,
                     file_path1=file_path1,
                     file_path2=file_path2,
                     move=move)
            d.update(file_change)
            file_changes.append(d)
    file_frame = pd.DataFrame(file_changes, columns=(
        'hexsha', 'file_path1', 'file_path2', 'move', 'lines', 'insertions',
        'deletions'))
    return file_frame


def get_commits(repo, revs, paths='', **kwargs):
    commits = []
    visited_commit_hexsha = set()
    for rev in revs:
        for commit in repo.iter_commits(rev=rev, paths=paths, **kwargs):
            commit_hexsha = commit.hexsha
            if commit_hexsha in visited_commit_hexsha:
                continue
            else:
                visited_commit_hexsha.add(commit_hexsha)
            commits.append(commit)
    return commits


def extract_actors(commits, actor_type, attrs):
    actor_attrs = ['{}.{}'.format(actor_type, attr) for attr in attrs]
    actors = su.dicts_to_dataframe(list(
        su.objs_to_dicts(commits, actor_attrs)))
    actors = actors.groupby(by=actor_attrs).size()
    actors = actors.reset_index().sort_values(actor_attrs)
    # noinspection PyTypeChecker
    new_columns = dict(list(zip(actor_attrs, attrs)) +
                       [(0, '{}_commits'.format(actor_type))])
    actors.rename(columns=new_columns, inplace=True)
    return actors


def commits_to_actor_frame(commits):
    attrs = ('name', 'email')
    authors = extract_actors(commits, 'author', attrs)
    committers = extract_actors(commits, 'committer', attrs)
    actors = pd.merge(authors, committers, on=attrs, how='outer')
    actors = actors.drop_duplicates().reset_index(drop=True).fillna(0)
    for attr in attrs:
        actors[attr] = su.categorize(actors[attr])
    for col_name in ('author_commits', 'committer_commits'):
        actors[col_name] = actors[col_name].astype('int')
    return actors


def connect_actors(actor_frame, connectivity_sets, connectivity_column):
    """
    :param actor_frame:
    :param connectivity_sets:
    :param connectivity_column:
    :return:

    Examples:

    same_actors = {
        'ccason': [3, 14, 15], 'clipka': [4, 5, 13],
        'wfpokorny': [11, 17], 'anshuarya': [0],
        'bentsm': [1], 'cbarton': [2], 'dbodor': [6],
        'jlecher': [7], 'jgrimbert': [8], 'nalvarez': [9],
        'selvik': [10], 'wverhelst': [12], 'gryken': [16],
        'github': [18]}
    actor_frame = connect_actors(actor_frame, same_actors, 'actor_id')
    """
    connectivity = {}
    for actor_id, connectivity_set in connectivity_sets.items():
        for actor in connectivity_set:
            connectivity[actor] = actor_id
    actor_frame[connectivity_column] = su.categorize(pd.Series(connectivity))
    return actor_frame


def combine_actors(actor_frame, connectivity_column):
    """

    :param actor_frame:
    :param connectivity_column:
    :return:

    Examples:
    combine_actors(actor_frame, 'actor_id')
    """
    aggregator = {'name': 'first', 'email': 'first',
                  'author_commits': 'sum',
                  'committer_commits': 'sum'}
    return actor_frame.groupby(connectivity_column).agg(aggregator)


def refs_to_ref_frame(git_refs):
    attrs = {'__class__.__name__': 'ref_type', 'name': 'name',
             'path': 'path', 'commit.hexsha': 'commit'}
    ref_frame = su.dicts_to_dataframe(list(
        su.objs_to_dicts(git_refs, attrs.keys())))
    ref_frame.rename(columns=attrs, inplace=True)
    return ref_frame


def commits_to_frame(commits):
    commit_attrs = (
        'hexsha', 'name_rev', 'size',
        'author.name', 'author.email',
        'authored_datetime', 'author_tz_offset',
        'committer.name', 'committer.email',
        'committed_datetime', 'committer_tz_offset',
        'encoding', 'message',
        'stats.total.files', 'stats.total.lines',
        'stats.total.insertions', 'stats.total.deletions',
        'stats.files')
    column_names = {attr: attr.replace('.', '_') for attr in commit_attrs}
    commit_frame = su.dicts_to_dataframe(list(
        su.objs_to_dicts(commits, commit_attrs)))
    commit_frame.rename(columns=column_names, inplace=True)
    commit_frame['name_rev'] = commit_frame['name_rev'].str.split(
        ' ', 1).apply(lambda x: x[-1])
    categorical_cols = (
        'name_rev', 'author_name', 'author_email',
        'committer_name', 'committer_email', 'encoding')
    for c in categorical_cols:
        commit_frame[c] = su.categorize(commit_frame[c])
    for c in ('authored_datetime', 'committed_datetime'):
        commit_frame[c] = commit_frame[c].astype('datetime64[ns]')
    commit_frame['message'] = commit_frame['message'].str.replace('\n', '\\n')
    commit_frame = commit_frame.sort_values(
        'committed_datetime', ascending=False).reset_index(drop=True)
    return commit_frame


def commit_parents_to_frame(commits):
    commit_parents = []
    for c in commits:
        hexsha = c.hexsha
        parent_hexshas = [p.hexsha for p in c.parents]
        if not len(parent_hexshas):
            commit_parents.append(dict(hexsha=hexsha, parent_hexsha=None))
        else:
            commit_parents.extend(
                (dict(hexsha=hexsha, parent_hexsha=p)
                 for p in parent_hexshas))
    return pd.DataFrame(commit_parents, columns=['hexsha', 'parent_hexsha'])


def insert_actor_ids(commit_frame, actor_frame, drop_name_email=True):
    actor_columns = ['author_name', 'author_email',
                     'committer_name', 'committer_email']
    cf = commit_frame[actor_columns]
    af = actor_frame[['name', 'email', 'actor_id']]
    author = pd.merge(
        cf, af, left_on=actor_columns[:2],
        right_on=('name', 'email'),
        how='left')['actor_id']
    committer = pd.merge(
        cf, af, left_on=actor_columns[2:],
        right_on=('name', 'email'),
        how='left')['actor_id']
    commit_frame.insert(3, 'author', author)
    commit_frame.insert(4, 'committer', committer)
    if drop_name_email:
        commit_frame.drop(actor_columns, axis=1, inplace=True)
    return commit_frame


def commit_trees_to_frame(commits):
    frame: pd.DataFrame = pd.concat(
        (commit_tree_to_frame(c) for c in commits))
    cat_columns = ('hexsha', 'tree', 'child', 'child_type')
    for col in cat_columns:
        frame[col] = su.categorize(frame[col])
    frame.reset_index(inplace=True, drop=True)
    return frame


def commit_tree_to_frame(commit):
    tree_dicts = []
    _add_subtree(tree_dicts, commit.tree, '.')
    tree_frame = pd.DataFrame(tree_dicts)
    tree_frame['hexsha'] = commit.hexsha
    tree_frame['child_type'] = su.categorize(tree_frame['child_type'])
    return tree_frame


def _add_subtree(tree_dicts, tree, tree_path):
    tree_dicts.extend((
        dict(tree=tree_path, child=subtree.path, child_type='tree')
        for subtree in tree.trees))
    tree_dicts.extend((
        dict(tree=tree_path, child=blob.path, child_type='blob')
        for blob in tree.blobs))
    for subtree in tree.trees:
        _add_subtree(tree_dicts, subtree, subtree.path)


def check_file_move(file_path):
    m = re.match(r'(.*)({.*\s=>\s.*\})(.*)', file_path)
    try:
        pre_part = m.group(1)
        change_part = m.group(2)
        post_part = m.group(3)
    except Exception:
        pre_part = ''
        change_part = file_path
        post_part = ''
    m = re.match(r'[{]?(.*)\s=>\s([^\}]*)[\}]?', change_part)
    try:
        old_part = m.group(1)
        new_part = m.group(2)
        old_file_name = combine_path_parts(pre_part, old_part, post_part)
        new_file_name = combine_path_parts(pre_part, new_part, post_part)
        return old_file_name, new_file_name
    except Exception:
        return change_part, change_part


def combine_path_parts(pre_part, inner_part, post_part):
    if inner_part:
        file_path = pre_part + inner_part + post_part
    elif pre_part.endswith('/') and post_part.startswith('/'):
        file_path = pre_part[:-1] + post_part
    else:
        file_path = pre_part + post_part
    return file_path


def build_file_move_graph(file_frame):
    move_frame = file_frame[file_frame.move]
    move_graph = nx.from_pandas_dataframe(
        move_frame,
        source='file_path1', target='file_path2',
        edge_attr='hexsha', create_using=nx.DiGraph())
    return move_graph


def build_merge_frame(commit_frame, parent_frame, min_parent_count=2):
    parent_count_frame = parent_frame.groupby('hexsha', as_index=False).agg(
        {'parent_hexsha': 'count'})
    multiparent_frame = parent_count_frame[
        parent_count_frame.parent >= min_parent_count]
    merge_frame = pd.merge(left=commit_frame,
                           right=multiparent_frame,
                           left_on='hexsha',
                           right_on='hexsha',
                           how='inner')
    return merge_frame
