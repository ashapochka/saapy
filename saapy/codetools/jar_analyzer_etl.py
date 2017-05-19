import xml.etree.ElementTree as et


class JarAnalyzerETL:
    def __init__(self, jar_analyzer_xml):
        self.jar_analyzer_xml = jar_analyzer_xml

    @staticmethod
    def jar_properties(jar):
        jar_name = jar.get("name")
        stats = jar.find("./Summary/Statistics")
        metrics = jar.find("./Summary/Metrics")
        class_count = int(stats.find("./ClassCount").text)
        abstract_class_count = int(stats.find("./AbstractClassCount").text)
        package_count = int(stats.find("./PackageCount").text)
        abstractness = float(metrics.find("./Abstractness").text)
        efferent = int(metrics.find("./Efferent").text)
        afferent = int(metrics.find("./Afferent").text)
        instability = float(metrics.find("./Instability").text)
        distance = float(metrics.find("./Distance").text)
        node_props = {
            "name": jar_name,
            "class_count": class_count,
            "abstract_class_count": abstract_class_count,
            "package_count": package_count,
            "abstractness": abstractness,
            "efferent": efferent,
            "afferent": afferent,
            "instability": instability,
            "distance": distance
        }
        return node_props

    def build_jar_deps_subgraph_from_jar_analyzer(self):
        # produced with JarAnalyzer 1.2
        deps_tree = et.parse(self.jar_analyzer_xml)
        root = deps_tree.getroot()
        jars = root.findall("./Jars/Jar")
        for jar in jars:
            # create jar node
            node_props = self.jar_properties(jar)
            jar_name = node_props["name"]
            query = """
            MERGE (jar:JarFile {
                name: {name},
                class_count: {class_count},
                abstract_class_count: {abstract_class_count},
                package_count: {package_count},
                abstractness: {abstractness},
                efferent: {efferent},
                afferent: {afferent},
                instability: {instability},
                distance: {distance}
            })
            """
            yield query, node_props
            # add jar packages
            for package in jar.findall("./Summary/Packages/Package"):
                package_name = package.text
                query = """
                MATCH (jar:JarFile {name: {jar_name}})
                MERGE (package:JavaPackage {
                    name: {package_name}
                })
                MERGE (jar)-[r:CONTAINS]->(package)
                """
                yield query, dict(jar_name=jar_name, package_name=package_name)
            # add jar unresolved deps
            packages = jar.findall("./Summary/UnresolvedDependencies/Package")
            for package in packages:
                package_name = package.text
                query = """
                MATCH (jar:JarFile {name: {jar_name}})
                MERGE (package:JavaPackage {
                    name: {package_name}
                })
                MERGE
                (jar)-[r:DEPENDS_UNRESOLVED]->(package)
                """
                yield query, dict(jar_name=jar_name, package_name=package_name)
            # add jar deps
            out_deps = jar.findall("./Summary/OutgoingDependencies/Jar")
            for out_jar in out_deps:
                out_jar_name = out_jar.text
                query = """
                MATCH (jar:JarFile {name: {jar_name}})
                MATCH (out_jar:JarFile {name: {out_jar_name}})
                MERGE
                (jar)-[r:DEPENDS]->(out_jar)
                """
                yield query, dict(jar_name=jar_name, out_jar_name=out_jar_name)
            in_deps = jar.findall("./Summary/IncomingDependencies/Jar")
            for in_jar in in_deps:
                in_jar_name = in_jar.text
                query = """
                MATCH (jar:JarFile {name: {jar_name}})
                MATCH (in_jar:JarFile {name: {in_jar_name}})
                MERGE
                (jar)-[r:DEPENDED_BY]->(in_jar)
                """
                yield query, {"jar_name": jar_name, "in_jar_name": in_jar_name}
            # add jar cycles
            cycles = jar.findall("./Summary/Cycles/Cycle")
            for cycle_jar in cycles:
                cycle_jar_name = cycle_jar.text
                query = """
                MATCH (jar:JarFile {name: {jar_name}})
                MATCH (cycle_jar:JarFile {name: {cycle_jar_name}})
                MERGE
                (jar)-[r:CYCLE]->(cycle_jar)
                """
                yield query, dict(jar_name=jar_name,
                                  cycle_jar_name=cycle_jar_name)
