import re
import textwrap

RST_RE = re.compile(
    r'(?P<before>'
    r'^(?P<indent> *)\.\. (code-block|sourcecode):: (python|pycon)\n'
    r'((?P=indent) +:.*\n)*'
    r'\n*'
    r')'
    r'(?P<code>(^((?P=indent) +.*)?\n)+)',
    re.MULTILINE,
)
INDENT_RE = re.compile('^ +(?=[^ ])', re.MULTILINE)
TRAILING_NL_RE = re.compile(r'\n+\Z', re.MULTILINE)

PYCON = ('>>> ', '... ',)


def find_sourcecode(src):
    for match in RST_RE.finditer(src):
        code = match['code']

        try:
            min_indent = min(INDENT_RE.findall(code))
        except ValueError:
            min_indent = ''

        if '>>>' in code:

            lines = []
            for line in code.split('\n'):
                for p in PYCON:
                    if p in line or line.endswith(p.strip()):
                        lines.append(line)
                        break

            code = '\n'.join(lines)
            code = code.replace('>>> ', '')
            code = code.replace('>>>', '')
            code = code.replace('... ', '')
            code = code.replace('...', '')

        code = textwrap.dedent(code)
        line_number = src[:match.start()].count('\n') + match['before'].count('\n')

        yield code.rstrip(), len(min_indent), line_number
