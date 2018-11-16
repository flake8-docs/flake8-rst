import operator
import doctest
import re

LINENO, SOURCE, RAW = range(3)

ROLE_RE = re.compile(r':flake8-(?P<role>\S*):\s?(?P<value>.*)$', re.MULTILINE)

INDENT_RE = re.compile(r'(?P<indent>^ *).', re.MULTILINE)

DEFAULT_IGNORED_LINES = [re.compile(r'^@(savefig\s|ok(except|warning))')]
DEFAULT_CONSOLE_SYSNTAX = [re.compile(r'^(%\S*\s)')]

IPYTHON_START_RE = re.compile(r'In \[(?P<lineno>\d+)\]:\s?(?P<code>.*\n)')
IPYTHON_FOLLOW_RE = re.compile(r'^\.{3}:\s?(?P<code>.*\n)')

ROLES = ['group', 'bootstrap']


def _match_default(match, group, default=None):
    try:
        return match.group(group)
    except IndexError:
        return default


def _extract_roles(match):
    role_block = _match_default(match, 'roles')
    roles = {}
    if not role_block:
        return roles
    for match in ROLE_RE.finditer(role_block):
        roles[match.group('role')] = match.group('value')
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
        self.ignore_lines_with = DEFAULT_IGNORED_LINES
        self.console_syntax = DEFAULT_CONSOLE_SYSNTAX

        self.roles.setdefault('group', 'None' if directive != 'ipython' else directive)
        if directive == "ipython":
            previous = self.roles.setdefault('add-ignore', '')
            if previous:
                self.roles['add-ignore'] += ', ' + 'E302, E305'
            else:
                self.roles['add-ignore'] = 'E302, E305'

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
            roles = _extract_roles(match)

            source_block = SourceBlock(self._boot_lines, self._source_lines[source_slice], directive=directive,
                                       language=language, roles=roles)
            source_block._remove_indentation()
            yield source_block

    def _remove_indentation(self):
        indentation = min(INDENT_RE.findall(self.source_block))
        if indentation:
            indent = len(indentation)
            source_lines = [(line[LINENO], line[SOURCE][indent:-1] + line[SOURCE][-1], line[RAW])
                            for line in self._source_lines]
            self._source_lines = source_lines

    def clean(self):
        for func in (self.clean_doctest, self.clean_ipython):
            source_lines = func()
            if source_lines:
                self._source_lines = source_lines
                break

        if self.directive == 'ipython' and self.language == 'python':
            self._source_lines = self.clean_console()

    def clean_doctest(self):
        try:
            lines = doctest.DocTestParser().get_examples(self.source_block)
        except ValueError:
            return None
        source_lines = []
        for line in lines:
            if self._should_ignore(line.source):
                continue
            src = self._remove_console_syntax(line.source)
            for i, source in enumerate(src.splitlines(True)):
                lineno, _, raw = self._source_lines[line.lineno + i]
                if source not in raw:
                    raise AssertionError
                source_lines.append((lineno, source, raw))

        return source_lines

    def clean_ipython(self):
        code_lines = []
        follow = 0
        for line in self._source_lines:
            match = IPYTHON_START_RE.match(line[SOURCE])
            if match and not self._should_ignore(match.group('code')):
                follow = len(match.group('lineno')) + 2
                src = self._remove_console_syntax(match.group('code'))
                code_lines.append((line[LINENO], src, line[RAW]))
                continue
            if not follow:
                continue
            match = IPYTHON_FOLLOW_RE.match(line[SOURCE][follow:])
            if match:
                code_lines.append((line[LINENO], match.group('code'), line[RAW]))
                continue
            follow = 0

        return code_lines

    def _should_ignore(self, source_line):
        for pattern in self.ignore_lines_with:
            if pattern.match(source_line):
                return True
        return False

    def _remove_console_syntax(self, source_line):
        for pattern in self.console_syntax:
            match = pattern.match(source_line)
            if match:
                return source_line.replace(match.group(1), '')
        return source_line

    def clean_console(self):
        source_lines = []
        for source_line in self._source_lines:
            source = source_line[SOURCE]
            if self._should_ignore(source):
                continue
            src = self._remove_console_syntax(source)
            if src == source:
                source_lines.append(source_line)
            else:
                source_lines.append((source_line[LINENO], src, source_line[RAW]))

        return source_lines
