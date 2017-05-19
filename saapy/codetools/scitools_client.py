# coding=utf-8
import contextlib
import logging
from tempfile import NamedTemporaryFile
from pathlib import Path

import subprocess

import shutil

import networkx as nx
from sortedcontainers import SortedSet

logger = logging.getLogger(__name__)


def und_tool_exists() -> bool:
    return shutil.which('und') is not None


class ScitoolsProject:
    code_graph: nx.MultiDiGraph
    metrics: dict
    root_path: Path
    root_arch_ids = None
    entity_kinds: SortedSet
    ref_kinds: SortedSet

    def __init__(self, root_path):
        self.code_graph = nx.MultiDiGraph()
        self.metrics = {}
        self.root_path = Path(root_path)
        self.root_arch_ids = []
        self.entity_kinds = SortedSet()
        self.ref_kinds = SortedSet()

    def populate(self, project_db):
        metric_names = project_db.metrics()
        self.metrics = project_db.metric(metric_names)
        self.root_arch_ids = self.add_architectures(project_db.root_archs())
        for entity in project_db.ents():
            self.add_entity(entity)

    def add_architectures(self, archs):
        arch_ids = []
        for arch in archs:
            arch_id = arch.longname()
            self.code_graph.add_node(arch_id,
                                     longname=arch.longname(),
                                     name=arch.name(),
                                     node_type='arch')
            arch_ids.append(arch_id)
            for ent in arch.ents():
                self.code_graph.add_edge(arch_id,
                                         self.get_node_id(ent),
                                         edge_type='contain')
            child_ids = self.add_architectures(arch.children())
            for child_id in child_ids:
                self.code_graph.add_edge(arch_id, child_id, edge_type='child')
                self.code_graph.add_edge(child_id, arch_id, edge_type='parent')
            for dependency in arch.depends():
                self.code_graph.add_edge(arch_id,
                                         dependency.longname(),
                                         edge_type='depend')
        return arch_ids

    def add_entity(self, ent):
        e = self.entity_to_dict(ent)
        node_id = self.get_node_id(ent_attrs=e)
        self.code_graph.add_node(node_id, attr_dict=e)
        self.entity_kinds.add(e['kind_longname'])
        parent = ent.parent()
        if parent:
            parent_id = self.get_node_id(ent=parent)
            self.code_graph.add_edge(node_id, parent_id,
                                     edge_type='parent')
        for ref in ent.refs():
            r = self.ref_to_dict(ref)
            self.code_graph.add_edge(node_id,
                                     self.get_node_id(ref.ent()),
                                     attr_dict=r)
            self.ref_kinds.add(r['kind_longname'])
        return node_id

    def ref_to_dict(self, ref):
        """

        :param ref:
        :return:
        """
        r = dict()
        r['column'] = ref.column()
        r['file'] = self.get_node_id(ref.file())
        # r['isforward'] = ref.isforward()
        r['kind_longname'] = ref.kind().longname().lower()
        r['name'] = ref.kindname().lower()
        r['line'] = ref.line()
        r['edge_type'] = 'ref'
        # r['macroexpansion'] = ref.macroexpansion()
        return r

    def get_node_id(self, ent=None, ent_attrs: dict=None):
        if ent and ent.kindname() == 'file':
            node_id = str(Path(ent.longname()).relative_to(
                self.root_path))
        elif ent:
            node_id = ent.uniquename()
        elif ent_attrs and ent_attrs['kindname'] == 'file':
            try:
                node_id = str(Path(ent_attrs['longname']).relative_to(
                    self.root_path))
            except ValueError:
                node_id = ent_attrs['longname']
        elif ent_attrs:
            node_id = ent_attrs['uniquename']
        else:
            node_id = None
        return node_id

    def entity_to_dict(self, ent):
        """

        :param ent:
        :return:
        """
        e = dict()
        e['ent_id'] = ent.id()
        e['parsetime'] = ent.parsetime()
        e['uniquename'] = ent.uniquename()
        e['longname'] = ent.longname()
        e['name'] = ent.name()
        e['relname'] = ent.relname()
        e['simplename'] = ent.simplename()
        e['kindname'] = ent.kindname().lower()
        e['kind_longname'] = ent.kind().longname().lower()
        e['parameters'] = ent.parameters(shownames=True)
        e['type'] = ent.type()
        e['value'] = ent.value()
        e['language'] = ent.language().lower()
        e['library'] = ent.library()
        metric_names = ent.metrics()
        e['metrics'] = ent.metric(metric_names)
        e['contents'] = ent.contents()
        e['comments'] = ent.comments()
        e['node_type'] = 'entity'
        # e['ib'] = ent.ib()
        # ent.depends()
        # ent.dependsby()
        # ent.ents(...)
        # ent.extname()
        # ent.filerefs(...)
        # ent.freetext(...)
        # ent.kind()
        # ent.lexer(...)
        return e


class ScitoolsClient:
    project_db = None
    project_path: Path

    def __init__(self, udb_path):
        try:
            import understand
            self.understand = understand
        except:
            logger.error(
                'scitools understand library is not found in python path')
        self.project_path = Path(udb_path).resolve()
        self.project_db = None
        if not und_tool_exists():
            logger.warning('und tool is not found on the path, '
                           'project modifications are disabled')

    def project_exists(self):
        return self.project_path.exists() and self.project_path.is_file()

    def create_project(self):
        subprocess.run(['und', 'create', str(self.project_path)], check=True)

    def open_project(self):
        """
        opens scitools understand database safely catching and printing possible
        UnderstandError
        :return: open database or None
        """
        self.close_project()
        try:
            self.project_db = self.understand.open(str(self.project_path))
        except self.understand.UnderstandError:
            self.project_db = None
            logger.exception('failed to open {}'.format(self.project_path))
        return self.project_db

    def close_project(self):
        if self.project_db is not None:
            self.project_db.close()
            self.project_db = None

    def add_files_to_project(self, file_paths):
        with NamedTemporaryFile(mode='w') as f:
            for file_name in file_paths:
                print(file_name, file=f, flush=True)
            files_file_name = '@{}'.format(f.name)
            subprocess.run(['und', 'add', files_file_name,
                            str(self.project_path)])

    def analyze_project(self):
        subprocess.run(['und', 'analyze', str(self.project_path)])

    def build_project(self, root_path):
        project = ScitoolsProject(root_path)
        project.populate(self.project_db)
        return project

    def remove_project(self):
        self.close_project()
        with contextlib.suppress(FileNotFoundError):
            self.project_path.unlink()


def inspect_refs(entity):
    """
    extracts basic information about all references from the inspected entity
    :param entity: inspected understand entity
    :return: list of tuples (ref kind name, ref entity kind name,
    ref entity long name, location line, location column)
    """
    return [(ref.kindname(),
             ref.ent().kindname(),
             ref.ent().longname(),
             ref.line(),
             ref.column()) for ref in entity.refs()]


def print_refs(entity):
    """
    prints basic information about all references from the inspected entity
    :param entity: inspected understand entity
    :return: list of tuples (ref kind name, ref entity kind name,
    ref entity long name, location line, location column)
    """
    ref_tuples = inspect_refs(entity)
    for r in ref_tuples:
        print("{0}, {1}, {2} at ({3}, {4})".format(*r))
    return ref_tuples
