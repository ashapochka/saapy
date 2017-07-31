# coding=utf-8
import csv
import glob
import json
import re
from datetime import datetime
from pathlib import Path
from typing import List

import pandas as pd


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


def regrep(file_pattern, search_pattern, recursive=True):
    for file_path in glob.iglob(file_pattern, recursive=recursive):
        with open(file_path, 'r') as f:
            for i, line in enumerate(f):
                line = line[:-1]
                if re.search(search_pattern, line):
                    yield (file_path, i, line)


def attr_to_value(obj, attr_path, default_value=None, sep='.', cache=None):
    attr_parts = attr_path.split(sep)
    cur_obj = obj
    attr_value = default_value
    for i, attr in enumerate(attr_parts):
        if cur_obj is None:
            break
        else:
            try:
                found_cached = False
                if cache is not None:
                    cur_path = sep.join(attr_parts[:i + 1])
                    if cur_path in cache:
                        attr_value = cache[cur_path]
                        found_cached = True
                if not found_cached:
                    if isinstance(cur_obj, dict):
                        attr_value = cur_obj[attr]
                    else:
                        attr_value = getattr(cur_obj, attr)
                    if cache is not None:
                        cache[cur_path] = attr_value
            except (AttributeError, KeyError):
                break
            else:
                cur_obj = attr_value
    else:
        return attr_value
    return default_value


def obj_to_dict(obj, attrs, default_value=None, sep='.',
                cache_attrs=True):
    attr_cache = {} if cache_attrs else None
    return {attr: attr_to_value(obj, attr,
                                default_value=default_value,
                                sep=sep, cache=attr_cache)
            for attr in attrs}


def objs_to_dicts(objs, attrs, default_value=None, sep='.', cache_attrs=True):
    """
    Extracts specified attributes 'attrs' from iterable 'objs'
    and returns them as dictionaries. Can traverse object trees splitting
    attributes by 'sep'.
    """
    return map(lambda obj: obj_to_dict(obj, attrs,
                                       default_value=default_value,
                                       sep=sep,
                                       cache_attrs=cache_attrs),
               objs)


def categorize(data):
    return data.astype('category')
