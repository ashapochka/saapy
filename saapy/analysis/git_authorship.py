# coding=utf-8
from typing import List
from toolz import pipe
import pyisemail
import pandas as pd
from fuzzywuzzy import fuzz
import networkx as nx
from sklearn.preprocessing import MinMaxScaler

from saapy.graphdb import Neo4jQueryFactory
from saapy.graphdb import Neo4jQueryAsyncInvoker
from .utils import (dicts_to_dataframe, dataframe_to_dicts, name_from_email)


class GitAuthorQueryFactory(Neo4jQueryFactory):
    def git_authors_query(self):
        return self.query("""
        MATCH (c:GitCommit:git$labels)
        RETURN DISTINCT
            c.author_name AS author_name,
            c.author_email AS author_email
        ORDER BY author_name""")

    def join_git_authors_to_commits(self):
        return self.query("""
        MATCH (a:GitAuthor:git$labels)
        MATCH (c:GitCommit:git$labels {
            author_name: a.author_name,
            author_email: a.author_email})
        CREATE (a)-[r:Authors]->(c)""")

    def join_similar_authors(self, similar_authors: List[dict]):
        q = """
        MATCH (a:GitAuthor:git$labels {
            author_name: params.author_name,
            author_email: params.author_email})
        MATCH (a_other:GitAuthor:git$labels {
            author_name: params.author_name_other,
            author_email: params.author_email_other})
        CREATE (a)-[r:Similar {
            same_email: params.same_email,
            email_name_similarity: params.email_name_similarity,
            name_similarity: params.name_similarity,
            name_to_email_similarity: params.name_to_email_similarity}
            ]->(a_other)
        """
        return self.batch_query(q, query_params=similar_authors)

    def author_ids_query(self):
        return self.query("""
        MATCH (a:GitAuthor:git$labels)
        RETURN id(a) AS author_id""")

    def similar_author_ids_query(self):
        return self.query("""
        MATCH (a1:GitAuthor:git$labels)-[:Similar]->(a2:GitAuthor$labels)
        RETURN id(a1) AS author_id, id(a2) AS similar_author_id
        """)

    def create_actors_query(self, actors: List[dict]):
        q = self.batch_query("""
        MATCH (pa:GitAuthor:git$labels)
        WHERE id(pa) = params.primary_id
        MATCH (a:GitAuthor:git$labels)
        WHERE id(a) IN params.group_ids
        WITH pa.author_name AS actor_name, COLLECT(a) AS authors
        CREATE (actor:Actor:analysis$labels {name: actor_name})
        FOREACH (author in authors | CREATE (actor)-[:Uses]->(author))
        """, query_params=actors)
        return q

    def select_actors_query(self, actors: List[dict]):
        q = self.batch_query("""
        MATCH (pa:GitAuthor:git$labels)
        WHERE id(pa) = params.primary_id
        MATCH (a:GitAuthor:git$labels)
        WHERE id(a) IN params.group_ids
        WITH pa.author_name AS actor_name, COLLECT(a.author_email) AS authors
        RETURN actor_name, authors
        """, query_params=actors)
        return q

    def analyze_package_usage_query(self):
        return self.query("""
        MATCH (a1:Actor)-->(p1:Package)<--(p2:Package)<--(a2:Actor)
        WHERE NOT "Travis" IN [a1.name, a2.name]
        WITH DISTINCT p1.longname AS package,
            p1.metric_CountDeclMethodPublic AS public_method_count,
            p1.metric_SumCyclomaticStrict AS total_cyclomatic_strict,
            COLLECT(DISTINCT a1.name) AS developers,
            COLLECT(DISTINCT a2.name) AS users,
            COLLECT(DISTINCT p2.longname) AS dependent_packages
        RETURN package, public_method_count, total_cyclomatic_strict,
            SIZE(developers) AS developer_count,
            SIZE(FILTER(user IN users WHERE NOT user IN developers))
            AS user_count,
            SIZE(dependent_packages) AS dependency_count
            ORDER BY package
        """)

    def create_git_author_nodes(self, enhanced_authors: List[dict]):
        return self.import_query(labels=['GitAuthor', 'git'],
                                 query_params=enhanced_authors)


class GitAuthorAnalysis:
    """
    performs analysis of git commit authors
    """

    def __init__(self,
                 project_labels,
                 invoker: Neo4jQueryAsyncInvoker,
                 query_timeout=None,
                 name_to_email_similarity_lower_boundary=70,
                 email_name_similarity_lower_boundary=70,
                 name_similarity_lower_boundary=70):
        self.name_to_email_similarity_lower_boundary = \
            name_to_email_similarity_lower_boundary
        self.email_name_similarity_lower_boundary = \
            email_name_similarity_lower_boundary
        self.name_similarity_lower_boundary = name_similarity_lower_boundary
        self.query_factory = GitAuthorQueryFactory(
            default_labels=project_labels)
        self.invoker = invoker
        self.query_timeout = query_timeout

    def create_git_authors(self):
        find_authors = self.query_factory.git_authors_query()
        authors_future = self.invoker.run(find_authors)
        authors = pipe(self.query_timeout,
                       authors_future.result,
                       dicts_to_dataframe,
                       self._enrich_authors)
        create_author_nodes = self.query_factory.create_git_author_nodes(
            authors)
        self.invoker.run(create_author_nodes).result(self.query_timeout)
        join_authors_to_commits = \
            self.query_factory.join_git_authors_to_commits()
        self.invoker.run(join_authors_to_commits).result(self.query_timeout)
        return authors

    def _enrich_authors(self, authors):
        def extract_name(x):
            is_valid_email = pyisemail.is_email(x['author_email'])
            email_name = x['author_email'].split('@')[
                0] if is_valid_email else ''
            name_from_email_name = name_from_email(email_name)
            return pd.Series([is_valid_email, email_name, name_from_email_name])

        newcols = authors.apply(extract_name, axis=1)
        newcols.columns = ['is_valid_email', 'email_name', 'name_from_email']
        newdf = authors.join(newcols)
        return newdf

    def _pair_authors(self, authors):
        authors_length = authors.shape[0]
        pairs = []
        for i in range(authors_length - 1):
            pairs.extend(((i, j) for j in range(i + 1, authors_length)))
        df = pd.DataFrame(pairs, columns=('author_idx', 'other_author_idx'))
        df = df.join(authors, on='author_idx')
        df = df.join(authors, on='other_author_idx', rsuffix='_other')
        return df

    def _compute_author_similarity(self, paired_authors):
        def row_similarity(row):
            same_email = row.author_email == row.author_email_other
            name_similarity = fuzz.token_set_ratio(row.author_name,
                                                   row.author_name_other)
            email_name_similarity = fuzz.ratio(row.email_name,
                                               row.email_name_other)
            name_to_email_similarity = fuzz.token_set_ratio(row.author_name,
                                                            row.name_from_email_other)
            return pd.Series(
                [same_email, name_similarity, email_name_similarity,
                 name_to_email_similarity])

        newcols = paired_authors.apply(row_similarity, axis=1)
        newcols.columns = ['same_email', 'name_similarity',
                           'email_name_similarity', 'name_to_email_similarity']
        newdf = paired_authors.join(newcols)
        return newdf

    def _select_similar_authors(self, authors):
        return authors[
            lambda df:
            df.same_email |
            (df.name_similarity >= self.name_similarity_lower_boundary) |
            (df.is_valid_email &
             ((df.email_name_similarity >=
               self.email_name_similarity_lower_boundary) | (
                  df.name_to_email_similarity >=
                  self.name_to_email_similarity_lower_boundary)))
        ]

    def cluster_similar_git_authors(self, authors):
        similar_authors = pipe(authors,
                               self._pair_authors,
                               self._compute_author_similarity,
                               self._select_similar_authors)
        join_similar_query = self.query_factory.join_similar_authors(
            similar_authors)
        self.invoker.run(join_similar_query).result(self.query_timeout)

    def create_actors(self):
        edges, nodes = self.select_similar_author_ids()
        actors = self._identify_actors(edges, nodes)
        create_actors_query = self.query_factory.create_actors_query(actors)
        create_actors_future = self.invoker.run(create_actors_query)
        create_actors_future.result(self.query_timeout)

    def select_similar_author_ids(self):
        author_ids_query = self.query_factory.author_ids_query()
        similar_author_ids_query = self.query_factory.similar_author_ids_query()
        author_ids_future, similar_author_ids_future = \
            self.invoker.run(author_ids_query, similar_author_ids_query)
        author_ids = author_ids_future.result(self.query_timeout)
        similar_author_pairs = similar_author_ids_future.result(
            self.query_timeout)
        nodes = [record["author_id"] for record in author_ids]
        edges = [(record["author_id"], record["similar_author_id"])
                 for record in similar_author_pairs]
        return edges, nodes

    def _identify_actors(self, edges, nodes):
        author_graph = nx.Graph()
        author_graph.add_nodes_from(nodes)
        author_graph.add_edges_from(edges)
        same_actor_groups = [list(g) for g in
                             nx.connected_components(author_graph)]
        actors = [dict(primary_id=int(g[0]), group_ids=[int(gid) for gid in g])
                  for g in same_actor_groups]
        return actors

    def create_git_authors_and_actors(self):
        authors = self.create_git_authors()
        self.cluster_similar_git_authors(authors)
        self.create_actors()

    def analyze_package_usage(self):
        package_usage_frame = self.get_package_usage_metrics()
        self.usage_by_package(package_usage_frame)

    def usage_by_package(self, package_usage_frame: pd.DataFrame):
        return package_usage_frame.set_index(['package'])

    def get_package_usage_metrics(self):
        package_usage_query = self.query_factory.analyze_package_usage_query()
        package_usage_future = self.invoker.run(package_usage_query)
        package_usage = package_usage_future.result(self.query_timeout)
        package_usage_frame = dicts_to_dataframe(package_usage)
        return package_usage_frame

    def normalized_usage_by_package(self, package_usage_frame: pd.DataFrame,
                                    drop_package_prefix: str = None):
        scaler = MinMaxScaler()
        df = package_usage_frame.drop('package', 1)
        df_scaled = pd.DataFrame(scaler.fit_transform(df), columns=df.columns)
        if drop_package_prefix:
            df_scaled['package'] = package_usage_frame['package'].apply(
                lambda text: text[text.startswith(drop_package_prefix)
                                  and len(drop_package_prefix):])
        else:
            df_scaled['package'] = package_usage_frame['package']
        df_sorted = df_scaled.sort_values('user_count').reset_index()
        del df_sorted['index']
        return df_sorted

    def plot_package_usage_bar(self, package_usage_frame: pd.DataFrame,
                               stacked: bool = True):
        ax = package_usage_frame.plot(kind='bar', stacked=stacked,
                                      width=1, figsize=(12, 10))
        ax.set_xticks(package_usage_frame.index)
        ax.set_xticklabels(package_usage_frame.package, rotation=90)
        ax.xaxis.set_tick_params(width=1)
