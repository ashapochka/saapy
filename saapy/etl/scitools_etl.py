# coding=utf-8

"""
implementation of ETL from scitools understand database to other storages
"""


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
        project = struct_db['scitools_project'] = []
        project.append(self.udb_to_struct())
        # archs = json_db.table('scitools_archs')
        # for arch in self.udb.archs():
        #     arch_struct = self.arch_to_struct(arch)
        #     archs.insert(arch_struct)
        entities = struct_db['scitools_entities'] = []
        refs = struct_db['scitools_refs'] = []
        for entity in self.udb.ents():
            entity_struct = self.entity_to_struct(entity)
            entities.append(entity_struct)
            for ref in entity.refs():
                ref_struct = self.ref_to_struct(ref)
                refs.append(ref_struct)
        return struct_db

    def udb_to_struct(self):
        """

        :return:
        """
        p = dict()
        p['name'] = self.udb.name()
        metric_list = self.udb.metrics()
        p['metric'] = self.udb.metric(metric_list)
        p['root_archs'] = [self.arch_to_struct(arch)
                           for arch in self.udb.root_archs()]
        return p

    @staticmethod
    def ref_to_struct(ref):
        """

        :param ref:
        :return:
        """
        r = dict()
        r['column'] = ref.column()
        r['referenced_entity_uniquename'] = ref.ent().uniquename()
        r['file_entity_uniquename'] = ref.file().uniquename()
        r['isforward'] = ref.isforward()
        r['kindname'] = ref.kindname()
        r['line'] = ref.line()
        r['referencing_entity_uniquename'] = ref.scope().uniquename()
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
        e['parsetime'] = ent.parsetime()
        e['uniquename'] = ent.uniquename()
        e['longname'] = ent.longname(True)
        e['name'] = ent.name()
        e['relname'] = ent.relname()
        e['simplename'] = ent.simplename()
        e['kindname'] = ent.kindname()
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
            e['metric.{0}'.format(key)] = value
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
    def import_to_neo4j(scitools_db: dict, neo4j_client, chunk_size=1000):
        query = "UNWIND {props} AS map CREATE (n:ScitoolsEntity) SET n = map"
        entities = scitools_db['scitools_entities']
        chunk_count = len(entities)/chunk_size + 1
        def batch():
            for i in range(0, len(entities), chunk_size):
                yield query, dict(props=entities[i:i + chunk_size])
        neo4j_client.run_in_tx(batch(), chunk_count=chunk_count)

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
