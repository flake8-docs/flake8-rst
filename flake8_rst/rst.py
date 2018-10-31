import itertools
import re

RST_RE = re.compile(
    r'(?P<before>'
    r'^(?P<indent> *)\.\. (?P<directive>code-block|sourcecode|ipython)::( (?P<language>i?python|pycon))?\n'
    r'((?P=indent) +:.*\n)*'
    r'\n*'
    r')'
    r'(?P<code>(^((?P=indent) {3}.*)?\n)+)',
    re.MULTILINE,
)

CONSOLE_RE = re.compile(
    r'(?P<before>\n?)'
    r'(?P<code>('
    r'^(?P<indent> *)>>> .*\n'
    r'^(((?P=indent)(>>>|...)(.*))?\n)+)'
    r')',
    re.MULTILINE,
)

INDENT_RE = re.compile('(?P<indent>^ +(?=[^ ]))', re.MULTILINE)
TRAILING_NL_RE = re.compile(r'\n+\Z', re.MULTILINE)

ANCHORS = (
    '>>> ', '... ',
    '>>>', '...',  # empty lines
)

DOCSTRING_RE = re.compile(
    r'(?P<before>\n?)'
    r'^(?P<code>((?P<indent> *)\"{3}.*\n(?:(?:(?P=indent).+)?\n)*(?P=indent)\"{3}))',
    re.MULTILINE,
)

JUPYTER_RE = re.compile(
    r'(?P<before>\n*)'
    r'^((?P<indent>(?:>{3}|\.{3}) ?)(?P<code>.*))$|^(?!>{3}|\.{3})(?P<comment>.*)$',
    re.MULTILINE,
)

IPYTHON_RE = re.compile(
    r'(?P<before>\n*)'
    r'^(?P<indent>(?:(?:In \[(\d+)\]:)|(?: +\.{4}:)) )(?P<code>.*)$|^(?!(In \[(\d+)\]:)|(?: +\.{4}:) )(?P<comment>.*)$',
    re.MULTILINE,
)

CONSOLE_EXPRESSIONS = (JUPYTER_RE, IPYTHON_RE)


def _strip_pycon(src, expression, indent, line_number):
    """Prepares code-blocks with code from console

    Matches each line to be either of form: '<indent> <code>' or '<comment>'
    Removes the <indent> block and comments out lines without <code>
    """

    # Inserting # in empty lines allows matching them as comments.
    # Therefore resulting code-block keeps its length and reported
    # line_numbers are correct.
    code_block = '\n#\n'.join(src.split('\n\n'))
    current_block = []
    found_console_code = False
    for match in re.finditer(expression, code_block):
        origin_code = match.group('code')
        indent_ = match.group('indent') or ''

        if origin_code is not None:
            current_block.append((_fix_consolespecific_syntax(origin_code), len(indent_)))
            found_console_code = True
        else:
            current_block.append(('#', 0))

    if found_console_code:
        code, indent_ = zip(*current_block)
        return "\n".join(code).rstrip(), indent + max(indent_), line_number
    else:
        raise ValueError


def _find_block(src, expression, indented_inside=False):
    for match in expression.finditer(src):
        origin_code = str(match.group('code'))
        try:
            if match.group('directive') == 'ipython' and match.group('language') == 'python':
                origin_code = _fix_consolespecific_syntax(origin_code)
        except IndexError:
            pass
        try:
            indentation = match.group('indent') if not indented_inside else min(INDENT_RE.findall(origin_code))
            indent = len(indentation or '')
        except ValueError:
            indent = 0
        block = "\n".join([line[indent:] for line in origin_code.split("\n")]).rstrip()
        line_number = src[:match.start()].count('\n') + match.group('before').count('\n')
        yield block, indent, line_number


def _fix_consolespecific_syntax(origin_code):
    origin_code = origin_code.replace('%timeit ', '_timeit_')
    origin_code = origin_code.replace('@savefig', '# avefig')
    return origin_code


def find_sourcecode(filename, src):
    contains_python_code = filename.split('.')[-1].startswith('py')
    code_blocks = _find_block(src, DOCSTRING_RE) if contains_python_code else [(src, 0, 0)]
    for block, indent, line_number in code_blocks:
        find_blocks = _find_block(block, RST_RE, indented_inside=True)
        if not contains_python_code:
            find_blocks = itertools.chain(_find_block(block, RST_RE, indented_inside=True),
                                          _find_block(block, CONSOLE_RE, indented_inside=True))
        for block_, indent_, line_number_ in find_blocks:
            for expression in (JUPYTER_RE, IPYTHON_RE):
                try:
                    yield (_strip_pycon(block_, expression, indent + indent_, line_number + line_number_))
                    break
                except ValueError:
                    pass
            else:
                yield block_, indent + indent_, line_number + line_number_
