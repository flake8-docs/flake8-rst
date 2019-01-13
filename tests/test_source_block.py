import doctest
import optparse
import pytest

try:
    import pathlib
except ImportError:
    import pathlib2 as pathlib

from flake8_rst.rst import RST_RE, apply_default_groupnames, apply_directive_specific_options, merge_by_group
from flake8_rst.sourceblock import SourceBlock, _extract_roles
from hypothesis import assume, given, note, example
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

    assert result == expected


@given(code_strategy)
def test_get_correct_line(src):
    code_block = SourceBlock.from_source('', src)

    for line_number, line in enumerate(src.splitlines(True), start=1):
        code_line = code_block.get_code_line(line_number)
        assert code_line['lineno'] == line_number
        assert code_line['source'] == line


def test_find_block():
    example = DATA_DIR / 'example_1.rst'
    src = example.open().read()

    code_block = SourceBlock.from_source('', src)

    for match, block in zip(RST_RE.finditer(src), code_block.find_blocks(RST_RE)):
        origin_code = match.group('code')
        origin_code = ''.join(map(lambda s: s.lstrip() + '\n', origin_code.splitlines()))
        assert block.source_block == origin_code


def test_clean_doctest():
    example = DATA_DIR / 'example_1.rst'
    src = example.open().read()

    code_block = SourceBlock.from_source('', src)

    for match, block in zip(RST_RE.finditer(src), code_block.find_blocks(RST_RE)):
        origin_code = match.group('code')
        origin_code = ''.join((line.source for line in doctest.DocTestParser().get_examples(origin_code)))

        assert block.clean_doctest()
        assert block.source_block == origin_code
        assert '>>>' not in origin_code


@pytest.mark.parametrize('src, expected', [
    (DATA_DIR / 'example_11.rst', "name = 'Brian'\nother = brian\n%timeit a = (1, 2,name)  # noqa: F821\n"
                                  "b = (3, 4, other)\nfor i in range(3):\n   print(a[i] is b[i])\n\n"),
    (".. ipython:: python\n   In [4]: grouped = df.groupby('A')\n\n   In [5]: for name, group in grouped:\n"
     "      ...:     print(name)\n      ...:     print(group)\n      ...:\n",
     "grouped = df.groupby('A')\nfor name, group in grouped:\n    print(name)\n    print(group)\n\n")
])
def test_clean_ipython(src, expected):
    if isinstance(src, pathlib.Path):
        src = src.open().read()

    code_block = SourceBlock.from_source('', src)

    block = next(code_block.find_blocks(RST_RE))

    assert block.clean_ipython()
    assert expected == block.source_block


@pytest.mark.parametrize('src, expected', [
    ('%timeit a = (1, 2,name)\n', 'a = (1, 2,name)\n'),
    ('%time a = (1, 2,name)\nb = (3, 4, other)\n', 'a = (1, 2,name)\nb = (3, 4, other)\n'),
])
def test_clean_console_syntax(src, expected):
    block = SourceBlock.from_source('', src)

    block.clean_console_syntax()
    block.clean_ignored_lines()

    assert block.source_block == expected


@pytest.mark.parametrize('src', [
    '%prun -l 4 f(x)\n',
    '%%timeit x = range(10000)\nmax(x)\n',
])
def test_ignore_unrecognized_console_syntax(src):
    block = SourceBlock.from_source('', src)

    block.clean_console_syntax()
    block.clean_ignored_lines()

    assert not block.source_block


@pytest.mark.parametrize('src, expected', [
    ('@okexcept\na = (1, 2,name)\n', 'a = (1, 2,name)\n'),
    ('@savefig "picture.png"\na = (1, 2,name)\nb = (3, 4, other)\n', 'a = (1, 2,name)\nb = (3, 4, other)\n'),
])
def test_clean_ignored_lines(src, expected):
    block = SourceBlock.from_source('', src)

    block.clean_ignored_lines()

    assert block.source_block == expected


@given(code_strategy, code_strategy, code_strategy)
def test_merge_source_blocks(bootstrap, src_1, src_2):
    block1 = SourceBlock.from_source(bootstrap, src_1)
    block2 = SourceBlock.from_source(bootstrap, src_2, len(src_1.splitlines()) + 1)
    expected = SourceBlock.from_source(bootstrap, src_1 + src_2)

    merged = SourceBlock.merge([block1, block2])
    reversed_merged = SourceBlock.merge([block1, block2])

    assert merged.complete_block == expected.complete_block
    assert reversed_merged.complete_block == expected.complete_block


@pytest.mark.parametrize("filename, directive, roles, default_groupnames, expected", [
    ('test.rst', 'code-block', {}, "*.rst->*: default", {'group': 'default'}),
    ('test.py', 'code-block', {}, "*.rst->*: default", {'group': 'None'}),
    ('test.rst', 'code-block', {}, "*->code-block: code-block, *->ipython: ipython", {'group': 'code-block'}),
    ('test.rst', 'ipython', {}, "*->code-block: code-block, *->ipython: ipython", {'group': 'ipython'}),
    ('test.py', 'code-block', {}, "last.py->code-block: code-block, *.rst->ipython: ipython", {'group': 'None'}),
])
def test_default_groupname(filename, directive, roles, default_groupnames, expected):
    func = apply_default_groupnames(lambda *a, **k: [SourceBlock([], [], directive=directive, roles=roles)])
    block = next(func(filename, options=optparse.Values(dict(default_groupnames=default_groupnames))))

    assert block.roles == expected


@pytest.mark.parametrize("directive, roles, expected", [
    ('code-block', {}, {}),
    ('ipython', {}, {'add-ignore': 'E302, E305'}),
    ('ipython', {'add-ignore': 'F'}, {'add-ignore': 'F, E302, E305'}),
])
def test_directive_specific_options(directive, roles, expected):
    func = apply_directive_specific_options(lambda *a, **k: [SourceBlock([], [], directive=directive, roles=roles)])
    block = next(func())

    assert block.roles == expected


@given(role=code_strategy, value=code_strategy, comment=code_strategy)
@example(role='group', value='Group#4', comment='Within 4th group.')
@pytest.mark.parametrize("string_format", [u'   :flake8-{role}:{value}\n',
                                           u'   :flake8-{role}:{value} #{comment}\n'])
def test_roles(string_format, role, value, comment):
    assume(role.strip() and value.strip() and comment.strip())
    role_string = string_format.format(role=role, value=value, comment=comment)
    note(role_string)
    roles = _extract_roles(role_string)

    assert value == roles[role]


@pytest.mark.parametrize("group_names, expected", [
    (['None', 'None'], ['None', 'None']),
    (['', ''], ['']),
    (['A', 'B', 'A'], ['A', 'B']),
    (['Ignore'], []),
])
def test_merge_by_group(group_names, expected):
    source_blocks = [SourceBlock([], [(0, '', '')], roles={'group': group}) for group in group_names]
    blocks = merge_by_group(lambda *a, **k: source_blocks)()
    result = sorted([block.roles['group'] for block in blocks])

    assert result == expected


@given(code_strategy, code_strategy, st.lists(code_strategy, min_size=1))
def test_inject_bootstrap_blocks(bootstrap, src, injected_bootstrap):
    note(injected_bootstrap)
    block = SourceBlock.from_source(bootstrap, src, roles={'bootstrap': '; '.join(injected_bootstrap)})
    expected = SourceBlock.from_source('\n'.join(injected_bootstrap), src)

    assert block.complete_block == expected.complete_block
