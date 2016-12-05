# coding=utf-8

import pytest
from pathlib import Path


@pytest.mark.integration
def test_work_directory():
    path = Path('.').resolve()
    print()
    print('work dir:', path)
