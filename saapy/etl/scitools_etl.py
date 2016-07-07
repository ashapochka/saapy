class ScitoolsETL:
    def __init__(self, udb):
        self.udb = udb

    def store_couples(self, run_query):
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
