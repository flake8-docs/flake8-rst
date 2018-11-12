import doctest

try:
    import pathlib
except ImportError:
    import pathlib2 as pathlib

from flake8_rst.rst import RST_RE
from flake8_rst.sourceblock import SourceBlock
from hypothesis import assume, given
from hypothesis import strategies as st

ROOT_DIR = pathlib.Path(__file__).parent
DATA_DIR = ROOT_DIR / 'data'

code_strategy = st.characters(blacklist_categories=['Cc'])


@given(code_strategy, code_strategy)
def test_from_sourcecode(bootstrap, src):
    assume(bootstrap and src)

    code_block = SourceBlock.from_source(bootstrap, src)

    expected = '\n'.join([bootstrap, src])
    result = code_block.complete_block

    assert expected == result


@given(code_strategy)
def test_get_correct_line(src):
    code_block = SourceBlock.from_source('', src)

    for line_number, line in enumerate(src.splitlines(True), start=1):
        code_line = code_block.get_code_line(line_number)
        assert line_number == code_line['lineno']
        assert line == code_line['source']


def test_find_block():
    example = DATA_DIR / 'example_1.rst'
    src = example.open().read()

    code_block = SourceBlock.from_source('', src)

    for match, block in zip(RST_RE.finditer(src), code_block.find_blocks(RST_RE)):
        origin_code = match.group('code')
        origin_code = ''.join(map(lambda s: s.lstrip() + '\n', origin_code.splitlines()))
        assert origin_code == block.source_block


def test_clean_doctest():
    example = DATA_DIR / 'example_1.rst'
    src = example.open().read()

    code_block = SourceBlock.from_source('', src)

    for match, block in zip(RST_RE.finditer(src), code_block.find_blocks(RST_RE)):
        origin_code = match.group('code')
        origin_code = ''.join((line.source for line in doctest.DocTestParser().get_examples(origin_code)))
        block.clean()
        assert origin_code == block.source_block
        assert '>>>' not in origin_code
