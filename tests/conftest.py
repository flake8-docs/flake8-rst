from __future__ import unicode_literals

import ast
import sys

try:
    import pathlib
except ImportError:
    import pathlib2 as pathlib
import pprint

import pytest

ROOT_DIR = pathlib.Path(__file__).parent
DATA_DIR = ROOT_DIR / 'data'
RESULT_DIR = ROOT_DIR / ('result_py%s' % (sys.version_info[0]))


@pytest.fixture()
def data_dir():
    return DATA_DIR


def read_ast(self):
    with self.open() as f:
        return ast.literal_eval(f.read())


def write_ast(self, data):
    if sys.version_info[0] < 3:
        o = 'wb'
    else:
        o = 'w'

    with self.open(o) as f:
        pprint.pprint(data, stream=f, width=120)


pathlib.Path.read_ast = read_ast
pathlib.Path.write_ast = write_ast


def pytest_addoption(parser):
    parser.addoption('--refresh', action='store_true', help='Refresh tests')


def pytest_generate_tests(metafunc):
    files = {}

    for f in list(DATA_DIR.glob('*')) + list(RESULT_DIR.glob('*')):
        name, number = f.stem.split('_')
        data = files.setdefault(number, [None, None])

        if name == 'example':
            i = 0
        elif name == 'result':
            i = 1
        else:
            raise ValueError('Not properly configured')

        data[i] = f

    if 'source' in metafunc.fixturenames:
        source = list(DATA_DIR.glob('*'))
        ids = [f.name for f in source]

        metafunc.parametrize('source', source, ids=ids)

    if 'checker' in metafunc.fixturenames and 'result' in metafunc.fixturenames:
        ids, values = zip(*files.items())
        metafunc.parametrize('checker,result', values, ids=ids, indirect=True)
