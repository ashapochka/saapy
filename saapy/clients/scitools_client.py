import understand
import sys
from traceback import print_exc


def safe_open_understand(dbpath):
    """
    opens scitools understand database safely catching and printing possible
    UnderstandError
    :param dbpath: local file path to the understand database
    :return: open database or None
    """
    try:
        db = understand.open(dbpath)
    except understand.UnderstandError:
        db = None
        print_exc(file=sys.stdout)
    return db


def inspect_refs(entity):
    """
    extracts basic information about all references from the inspected entity
    :param entity: inspected understand entity
    :return: list of tuples (ref kind name, ref entity kind name,
    ref entity long name, location line, location column)
    """
    return [(ref.kindname(),
             ref.ent().kindname(),
             ref.ent().longname(),
             ref.line(),
             ref.column()) for ref in entity.refs()]


def print_refs(entity):
    """
    prints basic information about all references from the inspected entity
    :param entity: inspected understand entity
    :return: list of tuples (ref kind name, ref entity kind name,
    ref entity long name, location line, location column)
    """
    ref_tuples = inspect_refs(entity)
    for r in ref_tuples:
        print("{0}, {1}, {2} at ({3}, {4})".format(*r))
    return ref_tuples
