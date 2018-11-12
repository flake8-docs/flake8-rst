import os
import sys

from flake8 import utils
from flake8.checker import FileChecker, Manager, LOG
from flake8.processor import FileProcessor

from flake8_rst.rst import find_sourcecode


class RstManager(Manager):

    def _job_count(self):
        return 0

    def make_checkers(self, paths=None):
        # type: (List[str]) -> NoneType
        """Create checkers for each file."""
        if paths is None:
            paths = self.arguments

        if not paths:
            paths = ['.']

        filename_patterns = self.options.filename
        running_from_vcs = self.options._running_from_vcs
        running_from_diff = self.options.diff

        # NOTE(sigmavirus24): Yes this is a little unsightly, but it's our
        # best solution right now.
        def should_create_file_checker(filename, argument):
            """Determine if we should create a file checker."""
            matches_filename_patterns = utils.fnmatch(
                filename, filename_patterns
            )
            is_stdin = filename == '-'
            file_exists = os.path.exists(filename)
            # NOTE(sigmavirus24): If a user explicitly specifies something,
            # e.g, ``flake8 bin/script`` then we should run Flake8 against
            # that. Since should_create_file_checker looks to see if the
            # filename patterns match the filename, we want to skip that in
            # the event that the argument and the filename are identical.
            # If it was specified explicitly, the user intended for it to be
            # checked.
            explicitly_provided = (not running_from_vcs and not running_from_diff and (argument == filename))
            return (file_exists and (explicitly_provided or matches_filename_patterns)) or is_stdin

        checks = self.checks.to_dictionary()

        checkers = []

        for argument in paths:
            for filename in utils.filenames_from(argument, self.is_path_excluded):
                if not should_create_file_checker(filename, argument):
                    continue
                checker = RstFileChecker(filename, checks, self.options)

                if not checker.should_process:
                    continue

                lines = checker.processor.read_lines()

                for code_block in find_sourcecode(filename, self.options.bootstrap, ''.join(lines)):
                    checker = RstFileChecker.from_sourcecode(
                        filename=filename, checks=checks, options=self.options,
                        code_block=code_block
                    )

                    checkers.append(checker)
        self.checkers = checkers

        LOG.info('Checking %d files', len(self.checkers))


class RstFileChecker(FileChecker):
    def __init__(self, filename, checks, options, code_block=None):
        self.code = code_block
        self.lines = code_block.complete_block.splitlines(True) if code_block else []
        super(RstFileChecker, self).__init__(filename, checks, options)

    @classmethod
    def from_sourcecode(cls, code_block, **kwargs):
        return RstFileChecker(code_block=code_block, **kwargs)

    def _make_processor(self):
        try:
            return FileProcessor(self.filename, self.options, lines=self.lines)
        except IOError:
            # If we can not read the file due to an IOError (e.g., the file
            # does not exist or we do not have the permissions to open it)
            # then we need to format that exception for the user.
            # NOTE(sigmavirus24): Historically, pep8 has always reported this
            # as an E902. We probably *want* a better error code for this
            # going forward.
            (exc_type, exception) = sys.exc_info()[:2]
            message = '{0}: {1}'.format(exc_type.__name__, exception)
            self.report('E902', 0, 0, message)
            return None

    def report(self, error_code, line_number, column, text, line=None):
        try:
            line = self.code.get_code_line(line_number)
            if line['lineno'] == 0:
                return error_code

            return super(RstFileChecker, self).report(error_code, line['lineno'], column + line['indent'],
                                                      text, line=line['raw_source'])
        except IndexError:
            return error_code
