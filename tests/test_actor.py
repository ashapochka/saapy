# coding=utf-8
from pathlib import Path

from saapy.analysis import ActorParser, csv_to_list

names_csv_path = Path('../data/names.csv')


def test_parse_email():
    names = csv_to_list(names_csv_path)
    parser = ActorParser()
    parser.add_role_names(names[1:])
    samples = ['john.smith@example.com',
               'john.smith257@example.com',
               'john.smith',
               'admin@example.com',
               'localdomain',
               'localdomain@localhost',
               'Jervis@example.com']
    print()
    for sample in samples:
        parsed_email = parser.parse_email(sample)
        print(parsed_email)
