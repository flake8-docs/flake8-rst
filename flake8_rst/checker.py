import optparse

from flake8.checker import FileChecker, Manager, LOG
from flake8.processor import FileProcessor
from flake8.style_guide import DecisionEngine

from .rst import find_sourcecode

ROLES = ['set-ignore', 'set-select', 'add-ignore', 'add-select']


class RstManager(Manager):

    def _job_count(self):
        return 0

    def make_checkers(self, paths=None):
        super(RstManager, self).make_checkers(paths)
        checkers = []
        for checker in self.checkers:
            src = ''.join(checker.processor.read_lines())
            for i, source_block in enumerate(find_sourcecode(checker.filename, checker.options, src)):
                checker = RstFileChecker.from_sourcecode(
                    filename=checker.filename, checks=checker.checks, options=self.options,
                    style_guide=self.style_guide, source_block=source_block
                )
                checkers.append(checker)

        self.checkers = checkers

        LOG.info('Checking %d blocks', len(self.checkers))


def inject_options(roles, options):
    new_options = optparse.Values(options.__dict__)
    for key in ('ignore', 'select'):

        if 'set-' + key in roles:
            values = [value.strip() for value in roles['set-' + key].split(',')]
            setattr(new_options, key, values)

        if 'add-' + key in roles:
            values = {value.strip() for value in roles['add-' + key].split(',')}
            values.update(new_options.__dict__[key])
            setattr(new_options, key, list(values))

    return new_options


class RstFileChecker(FileChecker):
    def __init__(self, filename, checks, options, style_guide=None, source_block=None):
        self.style_guide = style_guide
        self.source_block = source_block

        if source_block:
            options = inject_options(source_block.roles, options)

        if self.style_guide:
            self.decider = DecisionEngine(options)

        super(RstFileChecker, self).__init__(filename, checks, options)

    @classmethod
    def from_sourcecode(cls, style_guide, source_block, **kwargs):
        return RstFileChecker(style_guide=style_guide, source_block=source_block, **kwargs)

    def _make_processor(self):
        content = self.source_block.complete_block if self.source_block else ''
        return FileProcessor(self.filename, self.options, lines=content.splitlines(True))

    def report(self, error_code, line_number, column, text, line=None):
        try:
            line = self.source_block.get_code_line(line_number)
            if line['lineno'] == 0:
                return error_code

            return super(RstFileChecker, self).report(error_code, line['lineno'], column + line['indent'],
                                                      text, line=line['raw_source'])
        except IndexError:
            return error_code

    def __getattribute__(self, name):
        if name == 'results' and self.style_guide:
            self.style_guide.decider = self.decider
        return super(RstFileChecker, self).__getattribute__(name)
