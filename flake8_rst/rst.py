import ast
import re
from functools import wraps

from .sourceblock import SourceBlock

RST_RE = re.compile(
    r'(?P<before>'
    r'^(?P<indent> *)\.\. (?P<directive>code-block|sourcecode|ipython)::( (?P<language>i?python|pycon))?\n'
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


def merge_by_group(func):

    @wraps(func)
    def func_wrapper(*args, **kwargs):
        blocks = {}
        for block in func(*args, **kwargs):
            group = block.roles['group']
            if group != 'None':
                data = blocks.setdefault(group, [])
                data.append(block)
            else:
                yield block
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
    def get_groupname(block, default_groupnames, file_ext):
        if file_ext in default_groupnames:
            groupnames = default_groupnames[file_ext]
            if block.directive in groupnames:
                return groupnames[block.directive]
            elif 'all' in groupnames:
                return groupnames['all']

        return 'None'

    @wraps(func)
    def func_wrapper(*args, **kwargs):
        file_ext = args[0].split('.')[-1]
        default_groups = args[1].default_groupnames or "{'rst': {'all': 'default'}}"
        default_groupnames = ast.literal_eval(default_groups)

        for block in func(*args, **kwargs):
            block.roles.setdefault('group', get_groupname(block, default_groupnames, file_ext))
            yield block

    return func_wrapper


@apply_directive_specific_options
@merge_by_group
@apply_default_groupnames
def find_sourcecode(filename, options, src):
    contains_python_code = filename.split('.')[-1].startswith('py')
    source = SourceBlock.from_source(options.bootstrap, src)
    source_blocks = source.find_blocks(DOCSTRING_RE) if contains_python_code else [source]

    for source_block in source_blocks:
        code_blocks = source_block.find_blocks(RST_RE)
        found_code_block = False
        for code_block in code_blocks:
            found_code_block = True
            code_block.clean()
            yield code_block

        if not found_code_block:
            source_code = source_block.clean_doctest()
            if source_code:
                yield SourceBlock(source_block.boot_lines, source_code, roles=source_block.roles)
