import doctest
import pytest

try:
    import pathlib
except ImportError:
    import pathlib2 as pathlib

from flake8_rst.rst import RST_RE
from flake8_rst.sourceblock import SourceBlock
from hypothesis import assume, given, note
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


@given(code_strategy, code_strategy, code_strategy)
def test_merge_source_blocks(bootstrap, src_1, src_2):
    block1 = SourceBlock.from_source(bootstrap, src_1)
    block2 = SourceBlock.from_source(bootstrap, src_2, len(src_1.splitlines()) + 1)
    expected = SourceBlock.from_source(bootstrap, src_1 + src_2)

    merged = SourceBlock.merge([block1, block2])
    reversed_merged = SourceBlock.merge([block1, block2])

    assert expected.complete_block == merged.complete_block
    assert expected.complete_block == reversed_merged.complete_block


@pytest.mark.parametrize("src, expected", [
    (".. ipython:: python\n\n   code-line\n", {'group': 'ipython', 'add-ignore': 'E302, E305'}),
    (".. ipython:: python\n   :flake8-group: None\n   :flake8-add-ignore: C404\n\n   code-line\n",
     {'group': 'None', 'add-ignore': 'C404, E302, E305'}),
    (".. ipython:: python\n   :flake8-group: Anything\n\n   code-line\n",
     {'group': 'Anything', 'add-ignore': 'E302, E305'}),
    (".. ipython:: python\n   :flake8-group: Anything\n   :flake8-bootstrap: import something\n\n   code-line\n",
     {'bootstrap': 'import something', 'group': 'Anything', 'add-ignore': 'E302, E305'}),
    (".. code-block:: python\n\n   code-line\n", {'group': 'None'}),
    (".. code-block:: python\n   :flake8-group: test-123\n\n   code-line\n", {'group': 'test-123'}),
    (".. code-block:: python\n   :flake8-bootstrap: import numpy as np; import pandas as pd\n\n   code-line\n",
     {'bootstrap': 'import numpy as np; import pandas as pd', 'group': 'None'}),
])
def test_get_roles(src, expected):
    block = next(SourceBlock.from_source('', src).find_blocks(RST_RE))

    assert expected == block.roles


@given(code_strategy, code_strategy, st.lists(code_strategy, min_size=1))
def test_inject_bootstrap_blocks(bootstrap, src, injected_bootstrap):
    note(injected_bootstrap)
    block = SourceBlock.from_source(bootstrap, src, roles={'bootstrap': '; '.join(injected_bootstrap)})
    expected = SourceBlock.from_source('\n'.join(injected_bootstrap), src)

    assert expected.complete_block == block.complete_block
