# coding=utf-8
import os
import pytest

skip_on_travisciorg = pytest.mark.skipif(
    os.environ.get('TEST_ENV') == 'travisciorg',
    reason="running test suite on travis-ci.org"
)
