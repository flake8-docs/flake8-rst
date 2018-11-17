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


@merge_by_group
def find_sourcecode(filename, bootstrap, src):
    contains_python_code = filename.split('.')[-1].startswith('py')
    source = SourceBlock.from_source(bootstrap, src)
    source_blocks = source.find_blocks(DOCSTRING_RE) if contains_python_code else [source]

    for source_block in source_blocks:
        inner_blocks = source_block.find_blocks(RST_RE)
        found_inner_block = False
        for inner_block in inner_blocks:
            found_inner_block = True
            inner_block.clean()
            yield inner_block

        if not found_inner_block and source_block.clean_doctest():
            source_block.clean()
            yield source_block
