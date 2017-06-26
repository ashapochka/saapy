# coding=utf-8
from pprint import pprint

import pytest as pytest

from saapy.analysis import (LexemeParser, fuzzy_distance, flatten_parsed_lexeme,
                            split_lexeme)


def test_map_segment():
    parser = build_parser()
    print()
    sample_segments = ['configuration', 'config', 'dlg', 'dialog', 'dialo',
                       'class', 'clazz', 'money', 'maney', 'servise', 'service',
                       'php5', 'clas', 'lisp', 'facade']
    for segment in sample_segments:
        segment_map = parser.map_segment(segment, segment, dict_distance=75)
        pprint(segment_map)


def test_segment_lexeme():
    parser = build_parser()
    print()
    sample_lexemes = ['configclazz', 'configurationclazz', 'inventoryfacade',
                      'inventaryfacade', 'crudservise']
    for lexeme in sample_lexemes:
        lexeme_words = parser.segment_into_words(lexeme, lexeme)
        pprint(lexeme_words)


# @pytest.mark.skip
def test_split_lexeme():
    print()
    sample_lexemes = ['ConfigClazz', 'configurationclazz', 'inventoryfacade',
                      'inventary_facade', 'crud_servise', 'HL7Adapter',
                      'DataRepository']
    for lexeme in sample_lexemes:
        lexeme_words = split_lexeme(lexeme)
        pprint(lexeme_words)


def test_parse_lexeme():
    parser = build_parser()
    print()
    sample_lexemes = [
        'ConfigClazz', 'configurationclazz', 'inventoryfacade',
        'inventary_facade', 'crud_servise', 'HL7Adapter',
        'DataRepository', 'MicropaymentWebservice',
        'ServicePlugin '
        'space::build_Micropayment5HTMLServise_Adapter1(type="VISA", n)']
    for lexeme in sample_lexemes:
        lexeme_words = parser.parse_lexeme(lexeme)
        pprint(lexeme_words)
        pprint(flatten_parsed_lexeme(lexeme_words))


def test_parse_lexeme1():
    parser = build_parser()
    print()
    sample_lexemes = [
        'ComputeAverageTextureColours']
    for lexeme in sample_lexemes:
        lexeme_words = parser.parse_lexeme(lexeme)
        pprint(lexeme_words)
        pprint(flatten_parsed_lexeme(lexeme_words))


def build_parser():
    parser = LexemeParser()
    parser.add_terms({
        'dlg': 'dialog',
        'clazz': 'class',
        'many': 'money',
        'servise': 'service',
        'php5': None,
        'crud': None,
        'config': 'configuration',
        'html': None,
        'plugin': None,
        'colour': 'color',
        'colours': 'colors'
    })
    return parser


def test_fuzzy_distance():
    print()
    pprint(fuzzy_distance('clazz', ['class', 'claws', 'close']))
