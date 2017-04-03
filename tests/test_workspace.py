# coding=utf-8

import pytest
from pathlib import Path


@pytest.mark.integration
def test_work_directory():
    path = Path('.').resolve()
    print()
    print('work dir:', path)


def test_data_directory(data_directory):
    print()
    print('data_directory:', data_directory)


def test_neo4j_test_ws_dir(neo4j_test_ws_dir):
    print()
    print('neo4j_test_ws_dir:', neo4j_test_ws_dir)
