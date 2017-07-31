# coding=utf-8
from typing import List

import networkx as nx
import pyisemail
from fuzzywuzzy import fuzz
from recordclass import recordclass
import pandas as pd

import saapy.util as su
from .lexeme import cleanup_proper_name


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


PARSED_EMAIL_FIELDS = ['email', 'valid', 'name', 'domain', 'parsed_name']

ParsedEmail = recordclass('ParsedEmail', PARSED_EMAIL_FIELDS)

PARSED_NAME_FIELDS = ['name', 'name_type']

ParsedName = recordclass('ParsedName', PARSED_NAME_FIELDS)


def proper(name: ParsedName):
    return name.name_type == 'proper' or name.name_type == 'personal'


class Actor:
    name: str
    email: str
    actor_id: str
    parsed_email: ParsedEmail
    parsed_name: ParsedName

    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email
        self.actor_id = '{} <{}>'.format(name, email).lower()
        self.parsed_email = None
        self.parsed_name = None

    def __repr__(self):
        return "Actor('{}')".format(self.actor_id)


class ActorParser:
    role_names = None

    def __init__(self):
        self.role_names = dict()

    def add_role_names(self, name_roles):
        for name, role in name_roles:
            self.role_names[name] = role

    def parse_name(self, name: str) -> List[str]:
        """
        splits a name into parts separated by ., _, camel casing and 
        similar
        :param name: potentially human name
        :return: list of name parts
        """
        parsed_name = ParsedName(**su.empty_dict(PARSED_NAME_FIELDS))
        lower_name = name.lower()
        if lower_name in self.role_names:
            parsed_name.name_type = self.role_names[lower_name]
            parsed_name.name = lower_name
        else:
            parsed_name.name_type = 'proper'
            parsed_name.name = cleanup_proper_name(name)
        return parsed_name

    def parse_email(self, email: str) -> ParsedEmail:
        lower_email = email.lower()
        parsed_email = ParsedEmail(**su.empty_dict(PARSED_EMAIL_FIELDS))
        parsed_email.email = lower_email
        parsed_email.valid = pyisemail.is_email(lower_email)
        email_parts = lower_email.split('@')
        parsed_email.name = email_parts[0]
        if len(email_parts) == 2:
            parsed_email.domain = email_parts[1]
        else:
            parsed_email.domain = ''
        parsed_email.parsed_name = self.parse_name(parsed_email.name)
        return parsed_email

    def parse_actor(self, name: str, email: str, name_from_email=True) -> Actor:
        parsed_email = self.parse_email(email)
        if not name and name_from_email:
            name = parsed_email.parsed_name.name
        actor = Actor(name, email)
        actor.parsed_name = self.parse_name(name)
        actor.parsed_email = parsed_email
        return actor


ACTOR_SIMILARITY_FIELDS = ['possible',
                           'identical',
                           'same_name',
                           'same_email',
                           'same_email_name',
                           'name_ratio',
                           'email_name_ratio',
                           'email_domain_ratio',
                           'name1_email_ratio',
                           'name2_email_ratio',
                           'proper_name1',
                           'proper_name2',
                           'proper_email_name1',
                           'proper_email_name2',
                           'explicit']
ActorSimilarity = recordclass('ActorSimilarity', ACTOR_SIMILARITY_FIELDS)

ACTOR_SIMILARITY_SETTINGS_FIELDS = ['min_name_ratio',
                                    'min_email_domain_ratio',
                                    'min_email_name_ratio',
                                    'min_name_email_ratio']
ActorSimilaritySettings = recordclass('ActorSimilaritySettings',
                                      ACTOR_SIMILARITY_SETTINGS_FIELDS)


class ActorSimilarityGraph:
    actor_graph: nx.Graph
    settings: ActorSimilaritySettings

    def __init__(self, settings=None):
        self.actor_graph = nx.Graph()
        self.similarity_checks = [self.identical_actors,
                                  self.similar_emails,
                                  self.similar_proper_names]
        if settings is None:
            settings = ActorSimilaritySettings(min_name_ratio=55,
                                               min_email_domain_ratio=55,
                                               min_email_name_ratio=55,
                                               min_name_email_ratio=55)
        self.settings = settings

    def add_actor(self, actor: Actor, link_similar=True):
        if self.actor_graph.has_node(actor.actor_id):
            return
        self.actor_graph.add_node(actor.actor_id, actor=actor)
        for actor_id, actor_attrs in self.actor_graph.nodes_iter(data=True):
            if actor.actor_id == actor_id:
                continue
            other_actor = actor_attrs['actor']
            if link_similar:
                similarity = self.evaluate_similarity(actor, other_actor)
                if similarity.possible:
                    self.actor_graph.add_edge(actor.actor_id,
                                              other_actor.actor_id,
                                              similarity=similarity,
                                              confidence=None)

    def link_actors(self, actor1_id: str, actor2_id: str,
                    confidence: float = 1):
        self.actor_graph.add_edge(actor1_id, actor2_id, confidence=confidence)
        if 'similarity' not in self.actor_graph[actor1_id][actor2_id]:
            self.actor_graph[actor1_id][actor2_id]['similarity'] = None

    def unlink_actors(self, actor1_id: str, actor2_id: str):
        self.actor_graph.remove_edge(actor1_id, actor2_id)

    def evaluate_similarity(self, actor: Actor,
                            other_actor: Actor) -> ActorSimilarity:
        similarity = self.build_similarity(actor, other_actor)
        checks = list(self.similarity_checks)
        while not similarity.possible and len(checks):
            check = checks.pop()
            similarity.possible = check(similarity)
        return similarity

    def build_similarity(self, actor, other_actor):
        similarity = ActorSimilarity(**su.empty_dict(ACTOR_SIMILARITY_FIELDS))
        # run comparisons for similarity
        similarity.identical = (actor.actor_id == other_actor.actor_id)
        similarity.proper_name1 = proper(actor.parsed_name)
        similarity.proper_name2 = proper(other_actor.parsed_name)
        similarity.proper_email_name1 = proper(actor.parsed_email.parsed_name)
        similarity.proper_email_name2 = proper(
            other_actor.parsed_email.parsed_name)
        similarity.same_name = (actor.parsed_name.name ==
                                other_actor.parsed_name.name)
        similarity.name_ratio = self.compare_names(actor.parsed_name,
                                                   other_actor.parsed_name)
        similarity.same_email = (actor.parsed_email.email ==
                                 other_actor.parsed_email.email)
        similarity.email_domain_ratio = fuzz.ratio(
            actor.parsed_email.domain,
            other_actor.parsed_email.domain)
        similarity.same_email_name = (actor.parsed_email.parsed_name.name ==
                                      other_actor.parsed_email.parsed_name.name)
        similarity.email_name_ratio = self.compare_names(
            actor.parsed_email.parsed_name,
            other_actor.parsed_email.parsed_name)
        similarity.name1_email_ratio = self.compare_names(
            actor.parsed_name,
            other_actor.parsed_email.parsed_name)
        similarity.name2_email_ratio = self.compare_names(
            actor.parsed_email.parsed_name,
            other_actor.parsed_name)
        return similarity

    @staticmethod
    def compare_names(name1: ParsedName, name2: ParsedName):
        if proper(name1) and proper(name2):
            compare = fuzz.token_set_ratio
        else:
            compare = fuzz.ratio
        return compare(name1.name, name2.name)

    def similar_emails(self, s: ActorSimilarity):
        return (s.same_email or
                (s.email_domain_ratio >= self.settings.min_email_domain_ratio
                 and
                 s.email_name_ratio >= self.settings.min_email_name_ratio))

    def similar_proper_names(self, s: ActorSimilarity):
        return (s.proper_name1 and s.proper_name2 and
                (s.same_name or s.name_ratio >= self.settings.min_name_ratio))

    def similar_name_to_email(self, s: ActorSimilarity):
        return (s.name1_email_ratio >= self.settings.min_name_email_ratio or
                s.name2_email_ratio >= self.settings.min_name_email_ratio)

    @staticmethod
    def identical_actors(s: ActorSimilarity):
        return s.identical

    def group_similar_actors(self):
        similar_actor_groups = [list(g) for g in
                                nx.connected_components(self.actor_graph)]
        return similar_actor_groups

    def print_similarity_groups(self):
        similar_groups = self.group_similar_actors()
        for i, group in enumerate(similar_groups):
            if len(group) < 2:
                continue
            print('=== group', i, '===')
            for actor1_id, actor2_id, data in self.actor_graph.edges_iter(
                    nbunch=group, data=True):
                print(actor1_id, '->', actor2_id, data)
