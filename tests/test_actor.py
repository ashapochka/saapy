# coding=utf-8
import shelve
from pprint import pprint

from saapy.analysis import ActorParser, ActorSimilarityGraph
from saapy.util import csv_to_list
from .test_utils import skip_on_travisciorg


samples = [('John Smith', 'john.smith@example.com'),
           ('', 'john.smith257@example.com'),
           ('Smith', 'john.smith'),
           ('Ken Trove', 'admin@example.com'),
           ('localdomain', 'localdomain'),
           ('', 'localdomain@localhost'),
           ('jervis', 'Jervis@example.com')]


def test_parse_email(data_root):
    parser = build_parser(data_root)
    print()
    for sample in samples:
        parsed_email = parser.parse_email(sample[1])
        print(parsed_email)


def test_parse_actor(data_root):
    parser = build_parser(data_root)
    print()
    for sample in samples:
        actor = parser.parse_actor(*sample)
        print(actor.parsed_name, actor.parsed_email)


def build_parser(data_root):
    names = csv_to_list(data_root / 'names.csv')
    parser = ActorParser()
    parser.add_role_names(names[1:])
    return parser


def test_similarity_graph(data_root):
    parser = build_parser(data_root)
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
def test_shelve_similarity_graph(data_root):
    parser = build_parser(data_root)
    actors = [parser.parse_actor(*sample) for sample in samples]
    graph = ActorSimilarityGraph()
    for actor in actors:
        graph.add_actor(actor)
    with shelve.open(str(data_root / 'test-similarity_graph.shelve')) as db:
        db['similarity_graph'] = graph


@skip_on_travisciorg
def test_unshelve_similarity_graph(data_root):
    with shelve.open(str(data_root / 'test-similarity_graph.shelve')) as db:
        graph = db['similarity_graph']
    assert graph is not None
    print()
    actor_groups = graph.group_similar_actors()
    pprint(actor_groups)
