import re
import textwrap
from collections import deque

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
    r'(?P<code>'
    r'^(?:(?P<indent> *)(?:>{3}) ?.*\n)+'
    r'^(?:(?P=indent)(?:>{3}|\.{3}) ?.*\n)*'
    r')',
    re.MULTILINE,
)

INTERN_ANCHOR_RE = re.compile(
    r'(?P<before>'
    r'\n*'
    r')'
    r'^(?P<indent>(?:>{3}|\.{3}) ?)(?P<code>.*)$|^(?!>{3}|\.{3})$',
    re.MULTILINE,
)

ANCHOR_IN_RE = re.compile(
    r'(?P<before>'
    r'\n*'
    r')'
    r'^(?P<indent>(?:(?:In \[(\d+)\]:)|(?: +\.{4}:)) ?)(?P<code>.*)$|^(?!(?:In \[(\d+)\]:)|(?: +\.{4}:))$',
    re.MULTILINE,
)

EXPRESSIONS = [RST_RE, ANCHOR_RE]


def strip_pycon(src, indent, line_number, *expressions):
    matches = (match for expression in expressions for match in expression.finditer(src))
    result = []
    skipped_lines = 0
    for match in matches:
        try:
            origin_code = match.group('code')
            indent_ = len(match.group('indent'))

            for _ in range(skipped_lines):
                result.append(('# noqa', 0))
            skipped_lines = 0

            result.append((origin_code, indent_))
        except TypeError:
            if result:
                skipped_lines += 1

    if result:
        code, indent_ = zip(*result)
        print(src)
        print(indent)
        print("\n".join(code).rstrip())
        return "\n".join(code).rstrip(), indent + max(indent_), line_number
    else:
        raise AttributeError


def find_sourcecode(src):
    matches = (match for expression in EXPRESSIONS for match in expression.finditer(src))
    for match in matches:
        origin_code = match.group('code')

        try:
            indent = len(min(INDENT_RE.findall(origin_code)))
        except ValueError:
            indent = 0

        code = "\n".join([line[indent:] for line in origin_code.split("\n")])
        start__count = src[:match.start()].count('\n')
        before__count = match.group('before').count('\n')
        line_number = start__count + before__count

        try:
            yield strip_pycon(code, indent, line_number, INTERN_ANCHOR_RE, ANCHOR_IN_RE)
        except AttributeError:
            yield code.rstrip(), indent, line_number
