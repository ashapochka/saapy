# coding=utf-8
from typing import List

import networkx as nx
import pyisemail
from recordclass import recordclass
from toolz import *
from fuzzywuzzy import fuzz

from analysis import split_name_by_character_type, empty_dict

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


class ActorParser:
    role_names = None

    _transform = compose(' '.join,
                         partial(filter, lambda s: s.isalpha()),
                         split_name_by_character_type)

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
        parsed_name = ParsedName(**empty_dict(PARSED_NAME_FIELDS))
        lower_name = name.lower()
        if lower_name in self.role_names:
            parsed_name.name_type = self.role_names[lower_name]
            parsed_name.name = lower_name
        else:
            parsed_name.name_type = 'proper'
            parsed_name.name = self._transform(lower_name)
        return parsed_name

    def parse_email(self, email: str) -> ParsedEmail:
        parsed_email = ParsedEmail(**empty_dict(PARSED_EMAIL_FIELDS))
        parsed_email.email = email
        parsed_email.valid = pyisemail.is_email(email)
        email_parts = email.split('@')
        parsed_email.name = email_parts[0]
        if len(email_parts) == 2:
            parsed_email.domain = email_parts[1]
        else:
            parsed_email.domain = ''
        parsed_email.parsed_name  = self.parse_name(parsed_email.name)
        return parsed_email

    def parse_actor(self, name: str, email: str) -> Actor:
        actor = Actor(name, email)
        actor.parsed_name = self.parse_name(name)
        actor.parsed_email = self.parse_email(email)
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
            settings = ActorSimilaritySettings(min_name_ratio=50,
                                               min_email_domain_ratio=50,
                                               min_email_name_ratio=50,
                                               min_name_email_ratio=50)
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

    def link_same_actor(self, actor_id1: str, actor_id2: str,
                        confidence: float = 1):
        self.actor_graph.add_edge(actor_id1, actor_id2, confidence=confidence)
        if 'similarity' not in self.actor_graph[actor_id1][actor_id2]:
            self.actor_graph[actor_id1][actor_id2]['similarity'] = None

    def evaluate_similarity(self, actor: Actor,
                            other_actor: Actor) -> ActorSimilarity:
        similarity = self.build_similarity(actor, other_actor)
        checks = list(self.similarity_checks)
        while not similarity.possible or len(checks):
            check = checks.pop()
            similarity.possible = check(similarity)
        return similarity

    def build_similarity(self, actor, other_actor):
        similarity = ActorSimilarity(**empty_dict(ACTOR_SIMILARITY_FIELDS))
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
