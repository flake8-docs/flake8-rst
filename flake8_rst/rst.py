import re

RST_RE = re.compile(
    r'(?P<before>'
    r'^(?P<indent> *)\.\. (code-block|sourcecode|ipython)::( (i?python|pycon))?\n'
    r'((?P=indent) +:.*\n)*'
    r'\n*'
    r')'
    r'(?P<code>(^((?P=indent) +.*)?\n)+)',
    re.MULTILINE,
)

INDENT_RE = re.compile('^ +(?=[^ ])', re.MULTILINE)
TRAILING_NL_RE = re.compile(r'\n+\Z', re.MULTILINE)

ANCHORS = (
    '>>> ', '... ',
    '>>>', '...',  # empty lines
)

ANCHOR_RE = re.compile(
    r'(?P<before>.*\n)'
    r'(?P<code>^>{3} (.+\n)+)',
    re.MULTILINE,
)

JUPYTER_RE = re.compile(
    r'(?P<before>\n*)'
    r'^((?P<indent>(?:>{3}|\.{3}) ?)(?P<code>.*))$|^(?!>{3}|\.{3})(?P<output>.*)$',
    re.MULTILINE,
)

IPYTHON_RE = re.compile(
    r'(?P<before>\n*)'
    r'^(?P<indent>(?:(?:In \[(\d+)\]:)|(?: +\.{4}:)) ?)(?P<code>.*)$|^(?!In \[(\d+)\]:)|(?: +\.{4}:)(?P<output>.*)$',
    re.MULTILINE,
)

EXPRESSIONS = (RST_RE, ANCHOR_RE)
CONSOLE_EXPRESSIONS = (JUPYTER_RE, IPYTHON_RE)


def strip_pycon(src, indent, line_number):
    """Prepares code-blocks with code from console

    Matches each line to be either of form: '<indent> <code>' or '<comment>'
    Removes the <indent> block and comments out lines without <code>
    """

    # Inserting # in empty lines allow matching them as comments.
    # Therefore resulting code-block keeps its length and reported
    # line_numbers are correct.
    code_block = '\n#\n'.join(src.split('\n\n'))
    matches = (match for expression in CONSOLE_EXPRESSIONS for match in re.finditer(expression, code_block))
    current_block = []
    for match in matches:
        origin_code = match.group('code')
        indent_ = match.group('indent') or ''
        output = match.group('output')

        if origin_code is not None:
            current_block.append((origin_code, len(indent_)))
        elif current_block and output:
            current_block.append(('# ' + output if output != '#' else '#', 0))

    if current_block:
        code, indent_ = zip(*current_block)
        return "\n".join(code).rstrip(), indent + max(indent_), line_number
    else:
        raise ValueError('Could not find any code inside src.')


def find_sourcecode(src):
    matches = (match for expression in EXPRESSIONS for match in expression.finditer(src))
    for match in matches:
        origin_code = match.group('code')

        try:
            indent = len(min(INDENT_RE.findall(origin_code)))
        except ValueError:
            indent = 0

        code = "\n".join([line[indent:] for line in origin_code.split("\n")]).rstrip()
        start_count = src[:match.start()].count('\n')
        before_count = match.group('before').count('\n')
        line_number = start_count + before_count

        try:
            yield strip_pycon(code, indent, line_number)
        except ValueError:
            yield code, indent, line_number
