# coding=utf-8
from pathlib import Path

import pytest
import tempfile
import shutil
import os
# from saapy import Workspace


class _Datadir(object):
    def __init__(self, request):
        basedir = request.fspath.dirpath()
        datadir = basedir.join("data")

        self._datadirs = []

        for d in (basedir, datadir):
            testdir = d.join(request.module.__name__)
            if request.cls is not None:
                clsdir = testdir.join(request.cls.__name__)
                self._datadirs.extend([
                    clsdir.join(request.function.__name__),
                    clsdir
                ])
            else:
                self._datadirs.append(testdir.join(request.function.__name__))
            self._datadirs.append(testdir)
        self._datadirs.append(datadir)

    def __getitem__(self, path):
        for datadir in self._datadirs:
            datadir_path = datadir.join(path)
            if datadir_path.check():
                return datadir_path

        raise KeyError("File `%s' not found in any of the following datadirs: %s" % (path, self._datadirs))


@pytest.fixture(scope="session")
def data_directory(request, pytestconfig):
    return pytestconfig.rootdir.join('tests/data')


FIXTURE_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'data')


@pytest.fixture
def data_root():
    return Path(FIXTURE_DIR)


@pytest.fixture
@pytest.mark.datafiles(os.path.join(FIXTURE_DIR, 'neo4j-test-ws'))
def neo4j_test_ws_dir(datafiles):
    return datafiles


# @pytest.fixture(scope="session")
# def workspace(request, data_directory):
#     wsconf_file = data_directory.join("workspace.yaml")
#     temp_root = tempfile.mkdtemp()
#     ws = Workspace("saapy-test-ws",
#                    temp_root,
#                    "saapy-test-ws",
#                    configuration_text=wsconf_file.read_text("utf-8"))
#
#     def fin():
#         shutil.rmtree(temp_root)
#
#     request.addfinalizer(fin)
#     return ws  # provide the fixture value
