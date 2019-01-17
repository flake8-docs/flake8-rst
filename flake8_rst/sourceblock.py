import itertools
import sys

import doctest
import operator
import re

try:
    if sys.version_info > (3, 5):
        import IPython.core.inputtransformer2 as ipt

        transform_manager = ipt.TransformerManager()
        transform_manager.cleanup_transforms.clear()
        transform_cell = transform_manager.transform_cell
        RUN_MAGIC_RE = re.compile(r"get_ipython\(\)\.run_line_magic\('(?:time(?:it)?)', (?P<x>(['\"]))(.*)(?P=x)\)",
                                  re.MULTILINE)
    else:
        from IPython.core import inputsplitter as ipt

        transformer = ipt.IPythonInputSplitter()
        transform_cell = transformer.transform_cell
        RUN_MAGIC_RE = re.compile(r"get_ipython\(\)\.magic\(u(?P<x>(['\"]))(?:time(?:it)?) (.*)(?P=x)\)",
                                  re.MULTILINE)
except ImportError:
    ipt = transform_cell = None

LINENO, SOURCE, RAW = range(3)

ROLE_RE = re.compile(r':flake8-(?P<role>\S*):\s?(?P<value>.*)$', re.MULTILINE)

INDENT_RE = re.compile(r'(?P<indent>^ *).', re.MULTILINE)

DEFAULT_IGNORED_LINES = [re.compile(r'get_ipython\(\)|^@(savefig\s.*|ok(except|warning)|verbatim|doctest)$')]

IPYTHON_START_RE = re.compile(r'In \[(?P<lineno>\d+)\]:\s?(?P<code>.*\n)')
IPYTHON_FOLLOW_RE = re.compile(r'^\.{3}:\s?(?P<code>.*\n)')

ROLES = ['group', 'bootstrap']


def _match_default(match, group, default=None):
    try:
        return match.group(group)
    except IndexError:
        return default


def _extract_roles(role_block):
    roles = {}
    if not role_block:
        return roles
    for match in ROLE_RE.finditer(role_block):
        roles[match.group('role')] = match.group('value').partition(' #')[0].strip()
    return roles


class SourceBlock(object):
    @classmethod
    def from_source(cls, bootstrap, src, start_line=1, **kwargs):
        if bootstrap:
            boot_lines = SourceBlock.convert_bootstrap(bootstrap)
        else:
            boot_lines = []
        code_lines = [(i, line, line) for i, line in enumerate(src.splitlines(True), start=start_line)]
        return cls(boot_lines, code_lines, **kwargs)

    @staticmethod
    def convert_bootstrap(bootstrap, split='\n'):
        return [(0, line + '\n', line + '\n') for line in bootstrap.split(split)]

    @classmethod
    def merge(cls, source_blocks):
        """Merge multiple SourceBlocks together"""

        if len(source_blocks) == 1:
            return source_blocks[0]

        source_blocks.sort(key=operator.attrgetter('start_line_number'))
        main_block = source_blocks[0]
        boot_lines = main_block.boot_lines
        source_lines = [source_line for source_block in source_blocks for source_line in source_block.source_lines]

        return cls(boot_lines, source_lines, directive=main_block.directive,
                   language=main_block.language, roles=main_block.roles)

    def __init__(self, boot_lines, source_lines, directive='', language='', roles=None):
        self._boot_lines = boot_lines
        self._source_lines = source_lines
        self.directive = directive
        self.language = language
        self.roles = roles or {}

        if 'bootstrap' in self.roles:
            self._boot_lines = SourceBlock.convert_bootstrap(self.roles['bootstrap'], split='; ')

    @property
    def boot_lines(self):
        return self._boot_lines

    @property
    def source_lines(self):
        return self._source_lines

    @property
    def source_block(self):
        """Return code lines **without** bootstrap"""
        return "".join(line[SOURCE] for line in self._source_lines)

    @property
    def complete_block(self):
        """Return code lines **with** bootstrap"""
        return "".join(line[SOURCE] for line in self._boot_lines + self._source_lines)

    @property
    def start_line_number(self):
        return self._source_lines[0][LINENO]

    def get_code_line(self, lineno):
        all_lines = self._boot_lines + self._source_lines
        line = all_lines[lineno - 1]
        return {'lineno': line[LINENO], 'indent': len(line[RAW]) - len(line[SOURCE]),
                'source': line[SOURCE], 'raw_source': line[RAW]}

    def find_blocks(self, expression):
        src = self.source_block
        for match in expression.finditer(src):
            origin_code = str(match.group('code'))
            line_start = src[:match.start()].count('\n') + match.group('before').count('\n')
            source_slice = slice(line_start, line_start + len(origin_code.splitlines(True)))
            directive = _match_default(match, 'directive', '')
            language = _match_default(match, 'language', '')
            roles = _extract_roles(_match_default(match, 'roles'))

            source_block = SourceBlock(self._boot_lines, self._source_lines[source_slice], directive=directive,
                                       language=language, roles=roles)
            source_block.remove_indentation()
            yield source_block

    def remove_indentation(self):
        indentation = min(INDENT_RE.findall(self.source_block))
        if indentation:
            indent = len(indentation)
            source_lines = [(line[LINENO], line[SOURCE][indent:-1] + line[SOURCE][-1], line[RAW])
                            for line in self._source_lines]
            self._source_lines = source_lines

    def clean(self):
        for func in (self.clean_doctest, self.clean_ipython):
            if func():
                break

        self.clean_console_syntax()
        self.clean_ignored_lines()

    def clean_doctest(self):
        try:
            lines = doctest.DocTestParser().get_examples(self.source_block)
        except ValueError:
            return None

        source_lines = [source_line for line in lines
                        for source_line in self._overwritten_source(line.source, line.lineno)]

        if source_lines:
            self._source_lines = source_lines
            return True
        return False

    def clean_ipython(self):
        source_lines = []
        src = ''
        lineno = follow = None
        for i, line in enumerate(self._source_lines):
            match = IPYTHON_START_RE.match(line[SOURCE])
            if match:
                lineno = i if lineno is None else lineno
                follow = len(match.group('lineno')) + 2
                src += match.group('code')
                continue
            if not follow:
                continue
            match = IPYTHON_FOLLOW_RE.match(line[SOURCE][follow:])
            if match:
                src += match.group('code')
                continue

            source_lines.extend(self._overwritten_source(src, lineno))

            src = ''
            lineno = follow = None

        source_lines.extend(self._overwritten_source(src, lineno))

        if source_lines:
            self._source_lines = source_lines
            return True
        return False

    def clean_console_syntax(self):
        if not transform_cell:
            return False
        block = self.source_block
        source_block = transform_cell(block)
        source_block = re.sub(RUN_MAGIC_RE, r'\3', source_block)

        if block != source_block:
            self._source_lines = list(self._overwritten_source(source_block))
            return True
        return False

    def _overwritten_source(self, src, start_line=0):
        for line, (lineno, _, raw) in zip(src.splitlines(True), itertools.islice(self._source_lines, start_line, None)):
            if not line.startswith('get_ipython') and line not in raw:
                raise ValueError

            yield (lineno, line, raw)

    def clean_ignored_lines(self):
        for i, (_, source, _) in enumerate(self._source_lines):
            for pattern in DEFAULT_IGNORED_LINES:
                if pattern.match(source):
                    self._source_lines.pop(i)
