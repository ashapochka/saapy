# coding=utf-8
import contextlib
import shelve
from collections import OrderedDict
from pathlib import Path
from pprint import pprint

import sys
from typing import Iterable

from invoke import Program, task, Collection
from profilehooks import timecall, profile
import pandas as pd

from saapy.analysis import (ActorParser, csv_to_list, ActorSimilarityGraph)
from saapy.vcs import GitClient
from saapy.codetools import ScitoolsClient, ScitoolsProject


class Povray:
    root_path: Path
    git_repo_path: Path
    analysis_dir_path: Path
    shelve_db_path: Path
    scitools_udb_path: Path
    git_graph = None
    similarity_graph = None
    scitools_project = None
    scitools_client = None

    def __init__(self, root_dir):
        self.root_path = Path(root_dir).resolve()
        self.git_repo_path = self.root_path / 'povray'
        self.analysis_dir_path = self.root_path / 'povray-analysis'
        self.shelve_db_path = self.analysis_dir_path / 'povray.shelve'
        self.scitools_udb_path = self.analysis_dir_path / 'povray-master.udb'
        self.scitools_client = ScitoolsClient(self.scitools_udb_path)

    @timecall
    def build_git_graph(self):
        with shelve.open(str(self.shelve_db_path)) as db:
            git_client = GitClient(self.git_repo_path)
            git_graph = git_client.build_commit_graph()
            git_client.add_commit_tree(git_graph, ref_name='origin/master')
            db['git_graph'] = git_graph
        self.git_graph = git_graph

    @timecall
    def load_git_graph(self):
        with shelve.open(str(self.shelve_db_path)) as db:
            if 'git_graph' in db:
                self.git_graph = db['git_graph']
            else:
                self.git_graph = None
        return self.git_graph

    def collect_source_files(self):
        master_commit = self.git_graph.commit_node(
            ref_name='origin/master')['hexsha']
        return self.git_graph.collect_files(
            master_commit,
            tree_node='source',
            predicate=lambda f: f.endswith(('.cpp', '.h')))

    def source_commit_frame(self) -> pd.DataFrame:
        source_files = self.collect_source_files()
        frame = self.git_graph.file_commit_frame(source_files)
        return frame

    @timecall
    def build_similarity_graph(self):
        actor_parser = ActorParser()
        role_names = csv_to_list(Path('../data/names.csv'))
        actor_parser.add_role_names(role_names)
        actors = [actor_parser.parse_actor(
            self.git_graph.commit_graph.node[actor_id]['name'],
            self.git_graph.commit_graph.node[actor_id]['email'])
            for actor_id in self.git_graph.actors]
        similarity_graph = ActorSimilarityGraph()
        for actor in actors:
            similarity_graph.add_actor(actor)
        self.similarity_graph = similarity_graph

    @timecall
    def build_understand_project(self):
        if not self.scitools_client.project_exists():
            self.build_git_graph()
            source_files = self.collect_source_files()
            self.scitools_client.create_project()
            self.scitools_client.add_files_to_project(
                self.git_repo_path / f for f in source_files)
            self.scitools_client.analyze_project()

    @timecall
    def build_code_graph(self):
        if not self.scitools_client.project_exists():
            print('understand project does not exist, '
                  'first run "$ povray understand --build"')
        else:
            with shelve.open(str(self.shelve_db_path)) as db:
                self.scitools_client.open_project()
                self.scitools_project = self.scitools_client.build_project(
                    self.git_repo_path)
                self.scitools_client.close_project()
                db['code_graph'] = self.scitools_project
                print('loaded scitools project of size',
                      len(self.scitools_project.code_graph))
                print('entity kinds:', self.scitools_project.entity_kinds)
                print('ref kinds:', self.scitools_project.entity_kinds)

    @timecall
    def load_code_graph(self) -> ScitoolsProject:
        with shelve.open(str(self.shelve_db_path)) as db:
            if 'code_graph' in db:
                self.scitools_project = db['code_graph']
            else:
                self.scitools_project = None
        return self.scitools_project

    @timecall
    def entity_class_metrics(self):
        project = self.load_code_graph()
        entities = []
        entity_comments = []
        refs = []
        for node, data in project.code_graph.nodes_iter(data=True):
            if ('node_type' not in data
                or 'entity' != data['node_type']
                or 'kindname' not in data
                or 'class' not in data['kindname']
                or 'unknown' in data['kindname']
                or 'CountLineCode' not in data['metrics']
                or not data['metrics']['CountLineCode']):
                continue
            entity = {'name': data['name'],
                      'longname': data['longname'],
                      'kindname': data['kindname']}
            entity.update(data['metrics'])
            entities.append(entity)
            entity_comments.append({'name': data['longname'],
                                    'comments': data['comments']})
            entity_defs = []
            for origin, dest, ref_data in project.code_graph.out_edges_iter(
                    nbunch=node, data=True):
                dest_data = project.code_graph.node[dest]
                ref = {'origin': data['longname'],
                       'destination': dest_data['longname']
                       if 'longname' in dest_data else '',
                       'name': dest_data['name']
                       if 'name' in dest_data else '',
                       'dest_kind': dest_data['kindname']
                       if 'kindname' in dest_data else '',
                       'ref': ref_data['name']
                       if 'name' in ref_data else '',
                       'ref_kind': ref_data['kind_longname']
                       if 'kind_longname' in ref_data else ''}
                refs.append(ref)
                if 'c define' == ref['ref_kind']:
                    entity_defs.append(ref['name'])
            entity['defs'] = ' '.join(entity_defs)

        entity_frame = pd.DataFrame(data=entities)
        entity_comment_frame = pd.DataFrame(data=entity_comments)
        ref_frame = pd.DataFrame(data=refs)
        entity_frame.to_csv(
            self.analysis_dir_path / 'entities.csv', index=False)
        entity_comment_frame.to_csv(
            self.analysis_dir_path / 'entity-comments.csv', index=False)
        ref_frame.to_csv(
            self.analysis_dir_path / 'entity-refs.csv', index=False)


@task
def cleanup(ctx):
    pv = Povray(ctx.config.povray.parent_dir)
    with contextlib.suppress(FileNotFoundError):
        pv.shelve_db_path.unlink()
        pv.scitools_udb_path.unlink()


@task
def git_graph(ctx):
    pv = Povray(ctx.config.povray.parent_dir)
    pv.build_git_graph()
    print('git graph built and saved with',
          len(pv.git_graph.commit_graph), 'nodes')


@task
def sim_graph(ctx):
    pv = Povray(ctx.config.povray.parent_dir)
    if not pv.load_git_graph():
        print('git graph does not exist,'
              'first run "$ povray git_graph" to build it')
        return 1
    pv.build_similarity_graph()
    pv.similarity_graph.print_similarity_groups()


@task
def understand(ctx):
    pv = Povray(ctx.config.povray.parent_dir)
    pv.build_understand_project()


@task
def code_graph(ctx, build=False, load=False):
    pv = Povray(ctx.config.povray.parent_dir)
    if build:
        pv.build_code_graph()
    elif load:
        pv.load_code_graph()


@task
def metrics(ctx):
    pv = Povray(ctx.config.povray.parent_dir)
    pv.entity_class_metrics()


@task
def history(ctx):
    pv = Povray(ctx.config.povray.parent_dir)
    pv.load_git_graph()
    df = pv.source_commit_frame()
    print(df.corr(method='spearman'))



def main():
    program = Program(namespace=Collection.from_module(sys.modules[__name__]),
                      version='0.1.0')
    program.run()


if __name__ == '__main__':
    main()
