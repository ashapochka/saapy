# coding=utf-8

"""
implementation of ETL from scitools understand database to other storages
"""

from typing import List
from saapy.connectors import Neo4jClient
import logging


logger = logging.getLogger(__name__)


class ScitoolsETL:
    """
    transfers scitools understand database content to files and neo4j
    """

    def __init__(self, udb):
        self.udb = udb

    def transfer_to_struct_db(self, struct_db: dict) -> dict:
        """

        :param struct_db:
        """
        project = struct_db['ScitoolsProject'] = []
        project.append(self.udb_to_struct())
        # archs = json_db.table('scitools_archs')
        # for arch in self.udb.archs():
        #     arch_struct = self.arch_to_struct(arch)
        #     archs.insert(arch_struct)
        entities = struct_db['ScitoolsEntity'] = []
        refs = struct_db['ScitoolsRef'] = []
        for entity in self.udb.ents():
            entity_struct = self.entity_to_struct(entity)
            entities.append(entity_struct)
            for ref in entity.refs():
                if not ref.isforward():
                    continue
                ref_struct = self.ref_to_struct(ref)
                refs.append(ref_struct)
        return struct_db

    def udb_to_struct(self):
        """

        :return:
        """
        p = dict()
        p['name'] = self.udb.name()
        # p['ent_kinds'] = [kind.longname()
        #                   for kind in understand.Kind.list_entity()]
        # p['ref_kinds'] = [kind.longname()
        #                   for kind in understand.Kind.list_reference()]
        metric_list = self.udb.metrics()
        metric = self.udb.metric(metric_list)
        for key, value in metric.items():
            p['metric_{0}'.format(key)] = value
        # p['root_archs'] = [self.arch_to_struct(arch)
        #                    for arch in self.udb.root_archs()]
        return p

    @staticmethod
    def ref_to_struct(ref):
        """

        :param ref:
        :return:
        """
        r = dict()
        r['column'] = ref.column()
        r['ent_id'] = ref.ent().id()
        r['file_ent_id'] = ref.file().id()
        # r['isforward'] = ref.isforward()
        r['kind_longname'] = ref.kind().longname()
        r['name'] = ref.kindname()
        r['line'] = ref.line()
        r['scope_ent_id'] = ref.scope().id()
        # r['macroexpansion'] = ref.macroexpansion()
        return r

    def arch_to_struct(self, arch) -> dict:
        """

        :param arch:
        :return:
        """
        a = dict()
        a['longname'] = arch.longname()
        a['name'] = arch.name()
        a['parent_longname'] = arch.parent().longname() \
            if arch.parent() else None
        a['children'] = [self.arch_to_struct(child_arch)
                         for child_arch in arch.children()]
        a['ents'] = [ent.uniquename()
                     for ent in arch.ents()]
        return a

    @staticmethod
    def entity_to_struct(ent):
        """

        :param ent:
        :return:
        """
        e = dict()
        e['ent_id'] = ent.id()
        e['parsetime'] = ent.parsetime()
        e['uniquename'] = ent.uniquename()
        e['longname'] = ent.longname(True)
        e['name'] = ent.name()
        e['relname'] = ent.relname()
        e['simplename'] = ent.simplename()
        e['kindname'] = ent.kindname()
        e['kind_longname'] = ent.kind().longname()
        e['parameters'] = ent.parameters(shownames=True)
        e['type'] = ent.type()
        e['value'] = ent.value()
        e['language'] = ent.language()
        e['parent_uniquename'] = ent.parent().uniquename() \
            if ent.parent() else None
        e['library'] = ent.library()
        metric_list = ent.metrics()
        metric = ent.metric(metric_list)
        for key, value in metric.items():
            e['metric_{0}'.format(key)] = value
        # e['ib'] = ent.ib()
        e['contents'] = ent.contents()
        e['comments'] = ent.comments()
        # ent.depends()
        # ent.dependsby()
        # ent.ents(...)
        # ent.extname()
        # ent.filerefs(...)
        # ent.freetext(...)
        # ent.kind()
        # ent.lexer(...)
        return e

    @staticmethod
    def import_to_neo4j(scitools_db: dict, neo4j_client: Neo4jClient,
                        chunk_size: int = 1000, labels: List[str] = []):
        nodeset_names_to_import = ['ScitoolsProject',
                                   'ScitoolsEntity',
                                   'ScitoolsRef']
        for nodeset_name in nodeset_names_to_import:
            node_labels = [nodeset_name] + labels
            nodes = scitools_db[nodeset_name]
            logger.info('importing %s of %s', len(nodes), nodeset_name)
            neo4j_client.import_nodes(nodes, chunk_size=chunk_size,
                                      labels=node_labels)
            logger.info('imported %s', nodeset_name)

        logger.info('creating relationships between Refs and Ents in neo4j')
        neo4j_client.run_query("""
        MATCH(ref:ScitoolsRef{labels})
        WITH ref
        MATCH (ent:ScitoolsEntity{labels})
        WHERE ent.ent_id = ref.scope_ent_id
        WITH ent, ref
        CREATE (ent)-[r:Scopes]->(ref)
        """, labels)

        neo4j_client.run_query("""
        MATCH(ref:ScitoolsRef{labels})
        WITH ref
        MATCH (ent:ScitoolsEntity{labels})
        WHERE ent.ent_id = ref.ent_id
        WITH ent, ref
        CREATE (ref)-[r:Refs]->(ent)
        """, labels)

        neo4j_client.run_query("""
        MATCH(ref:ScitoolsRef{labels})
        WITH ref
        MATCH (ent:ScitoolsEntity{labels})
        WHERE ent.ent_id = ref.file_ent_id
        WITH ent, ref
        CREATE (ent)-[r:Includes]->(ref)
        """, labels)
        logger.info('created relationships between Refs and Ents in neo4j')

    def store_couples(self, run_query):
        """

        :param run_query:
        """
        java_files = self.udb.ents("Java File")
        for fent in java_files:
            pfent = fent.refs("Define", "Package")[0].ent()
            file_query = """
            MERGE (file:JavaFile {name: {file_name}})
            MERGE (package:JavaPackage {name: {package_name}})
            MERGE (file)-[r:DEFINES]->(package)
            """
            run_query(file_query, {"file_name": fent.relname(),
                                   "package_name": pfent.longname()})
            fmetrics = fent.metric(["CountLineCode", "SumCyclomaticStrict"])
            set_file_metrics_query = """
            MATCH (file: JavaFile {name: {file_name}})
            SET file.count_line_code = {count_line_code},
                file.sum_cyclomatic_strict = {sum_cyclomatic_strict}
            """
            run_query(set_file_metrics_query, {
                "file_name": fent.relname(),
                "count_line_code": fmetrics["CountLineCode"],
                "sum_cyclomatic_strict": fmetrics["SumCyclomaticStrict"]})
            for crel in fent.refs("Define", "Class, Interface"):
                cent = crel.ent()
                class_query = """
                MATCH (file:JavaFile {name: {file_name}})
                MATCH (package:JavaPackage {name: {package_name}})
                MERGE (class:JavaClass {name: {class_name}})
                MERGE (file)-[r:DEFINES]->(class)
                MERGE (package)-[r1:CONTAINS]->(class)
                """
                run_query(class_query, {
                    "file_name": fent.relname(),
                    "package_name": pfent.longname(),
                    "class_name": cent.longname()})
                for cprel in cent.refs("Couple"):
                    cpent = cprel.ent()
                    pent = cpent.parent()
                    while pent.parent() is not None and pent.kindname() != \
                            "File":
                        pent = pent.parent()
                    package_ent = pent.refs("Define", "Package")[0].ent()
                    if package_ent.longname() == "java.lang":
                        continue
                    run_query(file_query, {"file_name": pent.relname(),
                                           "package_name":
                                               package_ent.longname()})
                    run_query(class_query, {
                        "file_name": pent.relname(),
                        "package_name": package_ent.longname(),
                        "class_name": cpent.longname()})
                    couple_query = """
                    MATCH (from_class:JavaClass {name: {from_class_name}})
                    MATCH (to_class:JavaClass {name: {to_class_name}})
                    MERGE (from_class)-[r:COUPLES]->(to_class)
                    """
                    run_query(couple_query, {"from_class_name": cent.longname(),
                                             "to_class_name": cpent.longname()})
