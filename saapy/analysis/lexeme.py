# coding=utf-8
import functools
import re
from typing import List, Dict, Any, Optional
import enchant
from fuzzywuzzy import fuzz


def fuzzy_distance(word, words):
    return sorted(((w, fuzz.ratio(word, w)) for w in words),
                  key=lambda e: -e[1])


def flatten_parsed_lexeme(parsed_lexeme: List,
                          skip_miss: bool=False) -> List:
    words = []
    for parsed_segment in parsed_lexeme:
        for segment_map in parsed_segment[1]:
            if skip_miss and segment_map[0] == 'miss':
                continue
            elif segment_map[0] == 'miss':
                words.append(segment_map[1])
            else:
                words.append(segment_map[2])
    return words


space_camel_case = functools.partial(re.compile(
r"""
(            # start the group
    # alternative 1
(?<=[a-z]|[0-9])  # current position is preceded by a lower char
            # (positive lookbehind: does not consume any char)
[A-Z]       # an upper char
            #
|   # or
    # alternative 2
(?<!\A)     # current position is not at the beginning of the string
            # (negative lookbehind: does not consume any char)
[A-Z]       # an upper char
(?=[a-z])   # matches if next char is a lower char
            # lookahead assertion: does not consume any char
)           # end the group""",
flags=re.VERBOSE).sub, r' \1')


def split_camel_case(s: str) -> List[str]:
    return space_camel_case(s).split()


space_alnum = functools.partial(re.compile(r'(\W|[_])').sub, r' ')


def split_alnum(s: str) -> List[str]:
    return space_alnum(s).split()


def split_lexeme(s: str) -> List[str]:
    sublexemes = split_alnum(s)
    return sum((split_camel_case(sublexeme) for sublexeme in sublexemes), [])


drop_digits = functools.partial(re.compile(r'\d').sub, r'')
split_dot = functools.partial(re.compile(r'\.').split)
split_double_colon = functools.partial(re.compile(r'::').split)
split_slash = functools.partial(re.compile(r'/').split)


def split_file_path(s: str) -> Dict[str, Optional[Any]]:
    path_parts = split_slash(s)
    try:
        ext_index = path_parts[-1].rindex('.')
        name, ext = path_parts[-1][:ext_index], path_parts[-1][ext_index+1:]
    except ValueError:
        name, ext = path_parts[-1], None
    return dict(dirs=path_parts[:-1], name=name, ext=ext)


email_nickname_pattern = re.compile(r"[a-zA-Z]+(\w|\.|\-|')+")


def cleanup_proper_name(s):
    return drop_digits(' '.join(split_lexeme(s))).lower()


def like_nickname(s: str) -> bool:
    return email_nickname_pattern.fullmatch(s) is not None


class LexemeParser:
    terms = None
    word_dictionary = enchant.Dict("en_US")

    def __init__(self):
        self.terms = {}

    def add_terms(self, terms):
        self.terms.update(terms)

    def parse_lexeme(self, lexeme: str) -> List:
        lexeme_parts = split_lexeme(lexeme)
        parsed_lexeme = []
        for lexeme_part in lexeme_parts:
            segments = self.segment_into_words(lexeme_part)
            parsed_lexeme.append((lexeme_part, segments))
        return parsed_lexeme

    def split_into_words(self, lexeme: str,
                         camel_split: bool = True,
                         digit_split: bool = True) -> List[str]:
        """
        splits an input string into parts by camel case pattern,
        underscores, acronyms, digits, etc.
    
        Example:
    
        ss = [None, "", "ab de fg", "ab   de fg", "ab:cd:ef",
              "number5", "fooBar", "foo200Bar", "ASFRules"]
    
        for s in ss:
            print(split_by_character_type(s))
    
        []
        []
        ['ab', ' ', 'de', ' ', 'fg']
        ['ab', '   ', 'de', ' ', 'fg']
        ['ab', ':', 'cd', ':', 'ef']
        ['number', '5']
        ['foo', 'Bar']
        ['foo', '200', 'Bar']
        ['ASF', 'Rules']
    
        :param lexeme: input string
        :param camel_split: account for camel case if true
        :return: list of string parts
        """
        if not lexeme:
            return []
        parts = []
        token_start = 0
        for pos in range(1, len(lexeme)):
            if ((lexeme[pos].islower() and lexeme[pos - 1].islower()) or
                    (lexeme[pos].isupper() and lexeme[pos - 1].isupper()) or
                    (lexeme[pos].isdigit() and lexeme[pos - 1].isdigit()) or
                    (not lexeme[pos].isalnum() and not lexeme[
                            pos - 1].isalnum())):
                continue
            if camel_split and (lexeme[pos].islower()
                                and lexeme[pos - 1].isupper()):
                new_token_start = pos - 1
                if new_token_start != token_start:
                    parts.append(lexeme[token_start: new_token_start])
                    token_start = new_token_start
            else:
                parts.append(lexeme[token_start: pos])
                token_start = pos
        parts.append(lexeme[token_start: len(lexeme)])
        return parts

    def segment_into_words(self, lexeme: str, exclude=None,
                           term_distance:int=100,
                           dict_distance:int=100):
        """
        Segment a string of chars using the pyenchant vocabulary.
        Keeps longest possible words that account for all characters,
        and returns list of segmented words.
    
        :param lexeme: (str) The character string to segment.
        :param exclude: (set) A set of string to exclude from consideration.
                        (These have been found previously to lead to dead ends.)
                        If an excluded word occurs later in the string, this
                        function will fail.
        """
        segments = []

        if not exclude:
            exclude = set()

        working_chars = lexeme
        while working_chars:
            # iterate through segments of the chars starting with the longest
            # segment possible
            for i in range(len(working_chars), 1, -1):
                segment = working_chars[:i]
                if segment in exclude:
                    continue
                segment_map = self.map_segment(segment,
                                               term_distance=term_distance,
                                               dict_distance=dict_distance)
                if segment_map[2] is not None:
                    segments.append(segment_map)
                    working_chars = working_chars[i:]
                    break
            else:  # no matching segments were found
                if len(segments):
                    exclude.add(segments[-1][1])
                    return self.segment_into_words(lexeme, exclude=exclude,
                                                   term_distance=term_distance,
                                                   dict_distance=dict_distance)
                # let the user know a word was missing from the dictionary,
                # but keep the word
                return [('miss', lexeme, None)]
        return segments

    def map_segment(self, segment: str,
                    term_distance:int=100,
                    dict_distance:int=100):
        low_segment = segment.lower()
        low_digitfree_segment = drop_digits(low_segment)
        segment_map = None
        if low_segment in self.terms:
            segment_map = ('term', segment,
                           self.terms[low_segment] or low_segment)
        elif low_digitfree_segment in self.terms:
            segment_map = ('term', segment,
                           self.terms[low_digitfree_segment]
                           or low_digitfree_segment)
        elif len(self.terms) and term_distance < 100:
            distances = fuzzy_distance(low_segment, self.terms.keys())
            term_key = distances[0][0]
            if distances[0][1] >= term_distance:
                segment_map = ('term', segment,
                               self.terms[term_key] or term_key)
        if not segment_map:
            if self.word_dictionary.check(low_digitfree_segment):
                segment_map = ('dict', segment, low_digitfree_segment)
            elif dict_distance < 100:
                suggest = self.word_dictionary.suggest(low_digitfree_segment)
                distances = fuzzy_distance(
                    low_digitfree_segment,
                    (word for word in suggest if word.isalpha()))
                distance = distances[0][1] if len(distances) else 0
                if distance >= dict_distance:
                    correction = distances[0][0]
                    segment_map = ('corr', segment, correction, distances)
            segment_map = segment_map or ('miss', segment, None)
        return segment_map
