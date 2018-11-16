import tempfile

import pytest

from flake8_rst.sourceblock import SourceBlock


@pytest.fixture()
def options(mocker):
    return mocker.Mock(max_line_length=80, verbose=0, hang_closing=False, ignore=[])


@pytest.fixture()
def checks():
    from flake8.plugins.manager import Checkers

    return Checkers()


@pytest.fixture()
def checker(request, options, checks):
    from flake8_rst.rst import find_sourcecode
    from flake8_rst.checker import RstFileChecker

    with request.param.open() as f:
        for code_block in find_sourcecode(str(request.param), '', f.read()):
            return RstFileChecker.from_sourcecode(
                filename=__name__, checks=checks.to_dictionary(), options=options,
                style_guide=None, code_block=code_block)


@pytest.fixture()
def summary(request, options, checks):
    from flake8_rst.application import Application
    with tempfile.NamedTemporaryFile() as file:
        application = Application()
        application.initialize(["--output-file={}".format(file.name), "--show-source"])
        application.run_checks([str(request.param)])
        application.report()
        return file.read().decode('utf-8')


@pytest.fixture()
def result(request):
    if not request.param or not request.param.exists():
        return ()

    return request.param


def test_checker(request, checker, result):
    data = checker.run_checks()

    for obj in data:
        if isinstance(obj, list):
            obj.sort()

    if request.config.getoption('--refresh'):
        result.write_ast(data)

    assert data == result.read_ast()


def test_summary(request, summary, result):
    path_to_data, _, _ = summary.partition('data')
    data = './'.join(sorted(summary.split(path_to_data)))

    if request.config.getoption('--refresh'):
        result.write_text(data)

    expected = result.read_text()
    assert data == expected


def test_readline(source, checks, options):
    from flake8_rst.checker import RstFileChecker
    with source.open() as f:
        src = f.read()

    source_block = SourceBlock.from_source('', src)
    checker = RstFileChecker(str(source), checks, options, code_block=source_block)
    lines = checker.processor.read_lines()

    assert src == ''.join(lines)
