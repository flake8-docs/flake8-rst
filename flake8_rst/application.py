import argparse
import time

from flake8.main import options
from flake8.main.application import Application as Flake8Application
from flake8.options import manager

from . import __version__
from . import checker


class Application(Flake8Application):
    def __init__(self, program='flake8-rst', version=__version__):
        self.start_time = time.time()
        self.end_time = None  # type: float
        self.program = program
        self.version = version
        self.prelim_arg_parser = argparse.ArgumentParser(add_help=False)
        options.register_preliminary_options(self.prelim_arg_parser)

        # super(Application, self).__init__(program, version) doesn't work
        # because flake8 has hardcoded 'flake8' in this code snippet:
        self.option_manager = manager.OptionManager(
            prog=program,
            version=version,
            parents=[self.prelim_arg_parser],
        )
        options.register_default_options(self.option_manager)

        self.check_plugins = None  # type: plugin_manager.Checkers
        self.formatting_plugins = None  # type: plugin_manager.ReportFormatters
        self.formatter = None  # type: BaseFormatter
        self.guide = None  # type: style_guide.StyleGuideManager
        self.file_checker_manager = None  # type: checker.Manager
        self.options = None  # type: argparse.Namespace
        self.args = None  # type: List[str]
        self.result_count = 0
        self.total_result_count = 0
        self.catastrophic_failure = False
        self.running_against_diff = False
        self.parsed_diff = {}  # type: Dict[str, Set[int]]

        self.option_manager.add_option(
            '--bootstrap', default=None, parse_from_config=True,
            help='Bootstrap code snippets. Useful for add imports.',
        )
        self.option_manager.add_option(
            '--default-groupnames', default="*.rst->*: default", parse_from_config=True,
            help='Set default group names.', type='string',
        )

    def make_file_checker_manager(self):
        if self.file_checker_manager is None:
            self.file_checker_manager = checker.RstManager(
                style_guide=self.guide,
                arguments=self.args,
                checker_plugins=self.check_plugins,
            )
