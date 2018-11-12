import doctest
import re


class SourceBlock(object):

    @classmethod
    def from_source(cls, bootstrap, src, start_line=1):
        if bootstrap:
            boot_lines = [(0, line + '\n', line + '\n') for line in bootstrap.splitlines()]
        else:
            boot_lines = []
        code_lines = [(i, line, line) for i, line in enumerate(src.splitlines(True), start=start_line)]
        return cls(boot_lines, code_lines)

    def __init__(self, boot_lines, code_lines):
        self._boot_lines = boot_lines
        self._code_lines = code_lines

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
            yield SourceBlock(self._boot_lines, self._code_lines[code_slice])._remove_indentation()

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
        lines = doctest.DocTestParser().get_examples(self.source_block)
        code_lines = []
        for line in lines:
            for i, source in enumerate(line.source.splitlines(True)):
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
            if match:
                follow = len(match.group(1))
                code_lines.append((line[0], match.group(2), line[2]))
                continue
            if not follow:
                continue
            match = follow_re.match(line[1][follow:])
            if match:
                code_lines.append((line[0], match.group(1), line[2]))
                continue
            follow = 0

        return code_lines
