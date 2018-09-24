import pytest


@pytest.fixture()
def options():
    from unittest.mock import Mock

    return Mock(max_line_length=80, verbose=0)


@pytest.fixture()
def checks():
    from flake8.plugins.manager import Checkers

    return Checkers()


@pytest.fixture()
def checker(request, options, checks):
    from flake8_rst.checker import RstFileChecker
    from flake8_rst.rst import find_sourcecode

    with request.param.open() as f:
        for code, indent, line_number in find_sourcecode(f.read()):

            return RstFileChecker.from_sourcecode(
                filename=__name__, code=code, bootstrap=False,
                checks=checks.to_dictionary(), options=options,
                start=line_number, indent=indent,
            )


@pytest.fixture()
def result(request):
    if not request.param or not request.param.exists():
        return ()

    return request.param


def test_checker(request, checker, result):
    data = checker.run_checks()

    if request.config.getoption('--refresh'):
        result.write_ast(data)

    assert data == result.read_ast()
