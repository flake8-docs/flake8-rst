import doctest
import re


def _match_default(match, group, default=None):
    try:
        return match.group(group)
    except IndexError:
        return default


class SourceBlock(object):

    @classmethod
    def from_source(cls, bootstrap, src, start_line=1):
        if bootstrap:
            boot_lines = [(0, line + '\n', line + '\n') for line in bootstrap.splitlines()]
        else:
            boot_lines = []
        code_lines = [(i, line, line) for i, line in enumerate(src.splitlines(True), start=start_line)]
        return cls(boot_lines, code_lines)

    @classmethod
    def merge(cls, *source_blocks):
        """Merge multiple SourceBlocks together

        :type source_blocks: SourceBlock
        """
        main_block = source_blocks[0]
        boot_lines = main_block._boot_lines
        code_lines = []
        for source_block in source_blocks:
            if boot_lines != source_block._boot_lines:
                raise AssertionError('You cannot merge SourceBlocks with different bootstraps!')
            code_lines.extend(source_block._code_lines)
        code_lines.sort(key=lambda line: line[0])
        return cls(boot_lines, code_lines, main_block.directive, main_block.language)

    def __init__(self, boot_lines, code_lines, directive=None, language=None):
        self._boot_lines = boot_lines
        self._code_lines = code_lines
        self.directive = directive
        self.language = language
        self.ignore_lines_with = [re.compile(r'^@savefig\s')]
        self.console_syntax = [re.compile(r'^(%\S*\s)')]

    @property
    def source_block(self):
        """Return code lines **without** bootstrap"""
        return "".join((line[1] for line in self._code_lines))

    @property
    def complete_block(self):
        """Return code lines **with** bootstrap"""
        return "".join([line[1] for line in self._boot_lines]) + "".join([line[1] for line in self._code_lines])

    def get_code_line(self, lineno):
        all_lines = self._boot_lines + self._code_lines
        line = all_lines[lineno - 1]
        return {'lineno': line[0], 'indent': len(line[2]) - len(line[1]),
                'source': line[1], 'raw_source': line[2]}

    def find_blocks(self, expression):

        src = self.source_block
        for match in expression.finditer(src):
            origin_code = str(match.group('code'))
            line_start = src[:match.start()].count('\n') + match.group('before').count('\n')
            code_slice = slice(line_start, line_start + len(origin_code.splitlines(True)))
            directive = _match_default(match, 'directive')
            language = _match_default(match, 'language')
            yield SourceBlock(self._boot_lines, self._code_lines[code_slice],
                              directive=directive, language=language)._remove_indentation()

    def _remove_indentation(self):
        expression = re.compile('(?P<indent>^ *).', re.MULTILINE)
        indentation = min(expression.findall(self.source_block))
        if indentation:
            indent = len(indentation)
            code_lines = [(line[0], line[1][indent:-1] + line[1][-1], line[2]) for line in self._code_lines]
            self._code_lines = code_lines
        return self

    def clean(self):
        for func in (self.clean_doctest, self.clean_ipython):
            code_lines = func()
            if code_lines:
                self._code_lines = code_lines
                break

    def clean_doctest(self):
        try:
            lines = doctest.DocTestParser().get_examples(self.source_block)
        except ValueError:
            return None
        code_lines = []
        for line in lines:
            if self._should_ignore(line.source):
                continue
            src = self._remove_console_syntax(line.source)
            for i, source in enumerate(src.splitlines(True)):
                lineno, _, raw_code = self._code_lines[line.lineno + i]
                assert source in raw_code
                code_lines.append((lineno, source, raw_code))

        return code_lines

    def clean_ipython(self):
        start_re = re.compile('In \[(\d+)\]:\s?(.*\n)')
        follow_re = re.compile(' \.{4}:\s?(.*\n)')
        code_lines = []
        follow = 0
        for line in self._code_lines:
            match = start_re.match(line[1])
            if match and not self._should_ignore(match.group(2)):
                follow = len(match.group(1))
                src = self._remove_console_syntax(match.group(2))
                code_lines.append((line[0], src, line[2]))
                continue
            if not follow:
                continue
            match = follow_re.match(line[1][follow:])
            if match:
                code_lines.append((line[0], match.group(1), line[2]))
                continue
            follow = 0

        return code_lines

    def _should_ignore(self, code_line):
        for pattern in self.ignore_lines_with:
            if re.compile(pattern).match(code_line):
                return True
        return False

    def _remove_console_syntax(self, code_line):
        for pattern in self.console_syntax:
            match = re.compile(pattern).match(code_line)
            if match:
                return code_line.replace(match.group(1), '')
        return code_line
