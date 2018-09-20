import pathlib

import pytest

ROOT_DIR = pathlib.Path(__file__).parent
DATA_DIR = ROOT_DIR / 'data'
RESULT_DIR = ROOT_DIR / 'result'

@pytest.fixture()
def result_dir():
    return RESULT_DIR

def pytest_generate_tests(metafunc):
    fixtures = (
        ('sourcecode_python', list(DATA_DIR.glob('python.*'))),
        ('sourcecode_pycon', list(DATA_DIR.glob('pycon.*'))),
    )

    for name, files in fixtures:

        if name in metafunc.fixturenames:
            ids = [str(f.relative_to(ROOT_DIR)) for f in files]
            metafunc.parametrize(name, files, ids=ids)
