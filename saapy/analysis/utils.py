# coding=utf-8
import csv
import json
from datetime import datetime
from pathlib import Path
from typing import List

import pandas as pd


def split_name_by_character_type(name: str, camel: bool = True) -> List[str]:
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

    :param name: input string
    :param camel: account for camel case if true
    :return: list of string parts
    """
    if not name:
        return []
    parts = []
    token_start = 0
    for pos in range(1, len(name)):
        if ((name[pos].islower() and name[pos-1].islower()) or
            (name[pos].isupper() and name[pos-1].isupper()) or
            (name[pos].isdigit() and name[pos-1].isdigit()) or
            (not name[pos].isalnum() and not name[pos-1].isalnum())):
            continue
        if camel and name[pos].islower() and name[pos-1].isupper():
            new_token_start = pos - 1
            if new_token_start != token_start:
                parts.append(name[token_start: new_token_start])
                token_start = new_token_start
        else:
            parts.append(name[token_start: pos])
            token_start = pos
    parts.append(name[token_start: len(name)])
    return parts


def dicts_to_dataframe(records: List[dict]) -> pd.DataFrame:
    """
    converts a list of records as dictionaries with the same keys into
    pandas data frame setting column names from key names
    :param records: list of dictionaries to convert, keys should be the same
    :return: pandas data frame with columns named after keys and values set from
    dictionary values
    """
    if not records:
        df = pd.DataFrame()
    else:
        record_values = (r.values() for r in records)
        df = pd.DataFrame(record_values, columns=records[0].keys())
    return df


def dataframe_to_dicts(dataframe: pd.DataFrame) -> List[dict]:
    """
    converts a pandas data frame into the list of dictionaries
    :param dataframe: pandas data frame to convert
    :return: list of dictionaries with keys set from the data frame column
    names and values from the column values
    """
    return dataframe.to_dict(orient='records')


def serialize_datetime(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial
    raise TypeError("Type {} not serializable".format(type(obj)))


def dump_pretty_json(obj, f):
    path = to_path(f)
    if path:
        with path.open('w') as fp:
            json.dump(obj, fp, indent=4, default=serialize_datetime)
    else:
        fp = f
        json.dump(obj, fp, indent=4, default=serialize_datetime)


def to_path(file_path):
    if isinstance(file_path, str):
        path = Path(file_path)
    elif isinstance(file_path, Path):
        path = file_path
    else:
        path = None
    return path


def empty_dict(keys):
    return {key: None for key in keys}


def csv_to_list(file_path):
    with to_path(file_path).open(newline='') as f:
        return list(csv.reader(f, delimiter=','))
