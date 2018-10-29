import re
import textwrap

RST_RE = re.compile(
    r'(?P<before>'
    r'^(?P<indent> *)\.\. (code-block|sourcecode|ipython):: (python|pycon)\n'
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
    r'(?P<before>'
    r'(?P<code>('
    r'^(?P<indent> *)>>> .*\n'
    r'^(((?P=indent)(>>>|...)(.*))?\n)+)'
    r'))',
    re.MULTILINE,
)

EXPRESSIONS = (RST_RE, ANCHOR_RE)


def find_sourcecode(src):
    matches = (match for expression in EXPRESSIONS for match in expression.finditer(src))
    for match in matches:
        origin_code = match.group('code')

        try:
            min_indent = min(INDENT_RE.findall(origin_code))
        except ValueError:
            min_indent = ''

        indent = len(min_indent)
        code = textwrap.dedent(origin_code)

        if '>>>' in code:
            indent += 4
            lines = []

            for i, line in enumerate(code.split('\n')):
                for anchor in ANCHORS:
                    if line.startswith(anchor):
                        lines.append(line[len(anchor):])
                        break

            code = '\n'.join(lines)

        line_number = src[:match.start()].count('\n') + match.group('before').count('\n')

        yield code.rstrip(), indent, line_number
