from flake8.main import options
from flake8.main.application import Application as Flake8Application
from flake8.options import manager

from . import __version__
from . import checker


class Application(Flake8Application):
    def __init__(self, program='flake8-rst', version=__version__):
        super(Application, self).__init__(program, version)

        self.option_manager = manager.OptionManager(
            prog=program, version=version
        )
        self.option_manager.add_option(
            '--bootstrap', default=None, parse_from_config=True,
            help='Bootstrap code snippets. Useful for add imports.',
        )
        self.option_manager.add_option(
            '--default-groupnames', default="*.rst->*: default", parse_from_config=True,
            help='Set default group names.', type='string',
        )
        self.option_manager.add_option(
            '--check-languages', default=["python3", "py3", "pycon", "python", "py"], parse_from_config=True,
            help='List of highlight-languages which are checked when using literal code-blocks (::).', type='string',
        )
        self.option_manager.add_option(
            '--highlight-language', default="python3", parse_from_config=True,
            help='Default language when no `.. highlight::` directive was used yet. Corresponds to'
                 '`highlight-language` config variable of sphinx.', type='string',
        )
        options.register_default_options(self.option_manager)

    def make_file_checker_manager(self):
        if self.file_checker_manager is None:
            self.file_checker_manager = checker.RstManager(
                style_guide=self.guide,
                arguments=self.args,
                checker_plugins=self.check_plugins,
            )
