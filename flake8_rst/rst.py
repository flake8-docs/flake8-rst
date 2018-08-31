import re
import textwrap

RST_RE = re.compile(
    r'(?P<before>'
    r'^(?P<indent> *)\.\. (code-block|sourcecode):: python\n'
    r'((?P=indent) +:.*\n)*'
    r'\n*'
    r')'
    r'(?P<code>(^((?P=indent) +.*)?\n)+)',
    re.MULTILINE,
)
INDENT_RE = re.compile('^ +(?=[^ ])', re.MULTILINE)
TRAILING_NL_RE = re.compile(r'\n+\Z', re.MULTILINE)


def find_sourcecode(src):
    for match in RST_RE.finditer(src):
        min_indent = min(INDENT_RE.findall(match['code']))

        code = textwrap.dedent(match['code'])
        line_number = src[:match.start()].count('\n') + match['before'].count('\n')

        yield code.rstrip(), len(min_indent), line_number
