import itertools

import re
from fnmatch import fnmatch
from functools import wraps

from .sourceblock import SourceBlock

COMMENT_RE = re.compile(r'(#.*$)', re.MULTILINE)

RST_RE = re.compile(
    r'(?P<before>'
    r'^(?P<indent> *)\.\. (?P<directive>code-block|sourcecode|ipython)::( (?P<language>i?python|pycon))?\n'
    r'(?P<roles>(^(?P=indent) +:\S+:.*\n)*)'
    r'\n*'
    r')'
    r'(?P<code>(^((?P=indent) {3} *.*)?\n)+(^(?P=indent) {3} *.*(\n)?))',
    re.MULTILINE,
)

MARKER_RE = re.compile(
    r'(?P<before>'
    r'^(?P<indent> *)^(?!\.{2} ).*::$'
    r'(?P<roles>(^(?P=indent) +:\S+:.*\n)*)'
    r'\n*'
    r')'
    r'(?P<code>(^((?P=indent) {3} *.*)?\n)+(^(?P=indent) {3} *.*(\n)?))',
    re.MULTILINE,
)

DOCSTRING_RE = re.compile(
    r'(?P<before>\n?)'
    r'^(?P<code>((?P<indent> *)\"{3}.*\n(?:(?:(?P=indent).+)?\n)*(?P=indent)\"{3}))',
    re.MULTILINE,
)

HIGHLIGHT_RE = re.compile(r'^\.\. (?P<directive>highlight):: (?P<language>\w+)$', re.MULTILINE)


def merge_by_group(func):
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        blocks = {}
        for block in func(*args, **kwargs):
            group = block.roles['group']
            if group == 'None':
                yield block
            elif group == 'Ignore':
                continue
            else:
                data = blocks.setdefault(group, [])
                data.append(block)
        for merge_blocks in blocks.values():
            yield SourceBlock.merge(merge_blocks)

    return func_wrapper


def apply_directive_specific_options(func):
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        for block in func(*args, **kwargs):
            if block.directive == "ipython":
                previous = block.roles.setdefault('add-ignore', '')
                if previous:
                    block.roles['add-ignore'] += ', ' + 'E302, E305'
                else:
                    block.roles['add-ignore'] = 'E302, E305'
            yield block

    return func_wrapper


def apply_default_groupnames(func):
    def resolve_mapping(mappings, pattern, split):
        for entry in mappings:
            key, values = entry.split(split, 1)
            if fnmatch(pattern, key.strip()):
                yield values.strip()

    @wraps(func)
    def func_wrapper(filename, options, *args, **kwargs):
        default_groupnames = re.sub(COMMENT_RE, '', options.default_groupnames)
        lines = default_groupnames.split(',' if ',' in default_groupnames else '\n')
        groupnames = list(resolve_mapping(lines, filename, '->'))

        for block in func(filename, options, *args, **kwargs):
            groupname = next(resolve_mapping(groupnames, block.directive, ':'), 'None')
            block.roles.setdefault('group', groupname)
            yield block

    return func_wrapper


def should_check_for_literal_blocks(source_block, highlight_languages):
    return source_block.directive == 'highlight' and source_block.language in highlight_languages


@apply_directive_specific_options
@merge_by_group
@apply_default_groupnames
def find_sourcecode(filename, options, src):
    contains_python_code = filename.split('.')[-1].startswith('py')
    source = SourceBlock.from_source(options.bootstrap, src, language=options.highlight_language)
    source_blocks = source.find_blocks(DOCSTRING_RE) if contains_python_code else source.split_by(HIGHLIGHT_RE)

    highlight_languages = options.check_languages

    for source_block in source_blocks:
        search_expression = {RST_RE}
        if should_check_for_literal_blocks(source_block, highlight_languages):
            search_expression.add(MARKER_RE)

        found_inner_block = False
        for inner_block in itertools.chain.from_iterable((source_block.find_blocks(exp) for exp in search_expression)):
            found_inner_block = True
            inner_block.clean()
            yield inner_block

        if not found_inner_block and source_block.clean_doctest():
            source_block.clean()
            yield source_block
