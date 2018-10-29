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

INTERN_ANCHOR_RE = re.compile(
    r'(?P<before>\n*)'
    r'^((?P<indent>(?:>{3}|\.{3}) ?)(?P<code>.*))$|^(?!>{3}|\.{3})(?P<output>.*)$',
    re.MULTILINE,
)

ANCHOR_IN_RE = re.compile(
    r'(?P<before>'
    r'\n*'
    r')'
    r'^(?P<indent>(?:(?:In \[(\d+)\]:)|(?: +\.{4}:)) ?)(?P<code>.*)$|^(?!In \[(\d+)\]:)|(?: +\.{4}:)(?P<output>.*)$',
    re.MULTILINE,
)

EXPRESSIONS = [RST_RE, ANCHOR_RE]


def strip_pycon(src, indent, line_number, *expressions):
    has_stripped = False
    for code_block in src.split('\n\n'):
        matches = (match for expression in expressions for match in re.finditer(expression, code_block))
        current_block = []
        for match in matches:
            origin_code = match.group('code')
            indent_ = match.group('indent')
            output = match.group('output')

            if origin_code is not None:
                current_block.append((origin_code, len(indent_) if indent_ else 0))
            elif current_block and output:
                current_block.append(('# ' + output, 0))

        if current_block:
            has_stripped = True
            code, indent_ = zip(*current_block)
            yield "\n".join(code), indent + max(indent_), line_number
            line_number += len(current_block) + 1

    if not has_stripped:
        yield src, indent, line_number


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

        for code, indent, line_number in strip_pycon(code, indent, line_number, INTERN_ANCHOR_RE, ANCHOR_IN_RE):
            yield code.rstrip(), indent, line_number
