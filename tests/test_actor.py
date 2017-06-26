# coding=utf-8
import shelve
from pathlib import Path
from pprint import pprint

from saapy.analysis import (ActorParser, csv_to_list, ActorSimilarityGraph)
from .test_utils import skip_on_travisciorg

names_csv_path = Path('../data/names.csv')

samples = [('John Smith', 'john.smith@example.com'),
           ('', 'john.smith257@example.com'),
           ('Smith', 'john.smith'),
           ('Ken Trove', 'admin@example.com'),
           ('localdomain', 'localdomain'),
           ('', 'localdomain@localhost'),
           ('jervis', 'Jervis@example.com')]


def test_parse_email():
    parser = build_parser()
    print()
    for sample in samples:
        parsed_email = parser.parse_email(sample[1])
        print(parsed_email)


def test_parse_actor():
    parser = build_parser()
    print()
    for sample in samples:
        actor = parser.parse_actor(*sample)
        print(actor.parsed_name, actor.parsed_email)


def build_parser():
    names = csv_to_list(names_csv_path)
    parser = ActorParser()
    parser.add_role_names(names[1:])
    return parser


def test_similarity_graph():
    parser = build_parser()
    actors = [parser.parse_actor(*sample) for sample in samples]
    graph = ActorSimilarityGraph()
    for actor in actors:
        graph.add_actor(actor)
    print()
    for actor1_id, actor2_id, data in graph.actor_graph.edges_iter(data=True):
        print(actor1_id, actor2_id, data)
    actor_groups = graph.group_similar_actors()
    pprint(actor_groups)


@skip_on_travisciorg
def test_shelve_similarity_graph():
    parser = build_parser()
    actors = [parser.parse_actor(*sample) for sample in samples]
    graph = ActorSimilarityGraph()
    for actor in actors:
        graph.add_actor(actor)
    with shelve.open('data/test-similarity_graph.shelve') as db:
        db['similarity_graph'] = graph


@skip_on_travisciorg
def test_unshelve_similarity_graph():
    with shelve.open('data/test-similarity_graph.shelve') as db:
        graph = db['similarity_graph']
    assert graph is not None
    print()
    actor_groups = graph.group_similar_actors()
    pprint(actor_groups)
