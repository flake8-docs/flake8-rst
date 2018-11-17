import doctest
import optparse
import pytest

try:
    import pathlib
except ImportError:
    import pathlib2 as pathlib

from flake8_rst.rst import RST_RE, apply_default_groupnames, apply_directive_specific_options
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


@pytest.mark.parametrize("filename, directive, roles, default_groupnames, expected", [
    ('*.rst', 'code-block', {}, None, {'group': 'default'}),
    ('*.py', 'code-block', {}, None, {'group': 'None'}),
    ('*.rst', 'code-block', {}, {'rst': {'ipython': 'ipython', '*': 'code-block'}}, {'group': 'code-block'}),
    ('*.rst', 'ipython', {}, {'*': {'ipython': 'ipython', 'code-block': 'code-block'}}, {'group': 'ipython'}),
    ('*.py', 'code-block', {}, {'rst': {'ipython': 'ipython', 'code-block': 'code-block'}}, {'group': 'None'}),
    ('*.py', 'ipython', {}, {'rst': {'ipython': 'ipython', 'code-block': 'code-block'}}, {'group': 'None'}),
])
def test_default_groupname(filename, directive, roles, default_groupnames, expected):
    func = apply_default_groupnames(lambda *a, **k: [SourceBlock([], [], directive=directive, roles=roles)])
    block = next(func(filename, options=optparse.Values(dict(default_groupnames=default_groupnames))))

    assert expected == block.roles


@pytest.mark.parametrize("directive, roles, expected", [
    ('code-block', {}, {}),
    ('ipython', {}, {'add-ignore': 'E302, E305'}),
    ('ipython', {'add-ignore': 'F'}, {'add-ignore': 'F, E302, E305'}),
])
def test_directive_specific_options(directive, roles, expected):
    func = apply_directive_specific_options(lambda *a, **k: [SourceBlock([], [], directive=directive, roles=roles)])
    block = next(func())

    assert expected == block.roles


@given(code_strategy, code_strategy, st.lists(code_strategy, min_size=1))
def test_inject_bootstrap_blocks(bootstrap, src, injected_bootstrap):
    note(injected_bootstrap)
    block = SourceBlock.from_source(bootstrap, src, roles={'bootstrap': '; '.join(injected_bootstrap)})
    expected = SourceBlock.from_source('\n'.join(injected_bootstrap), src)

    assert expected.complete_block == block.complete_block
