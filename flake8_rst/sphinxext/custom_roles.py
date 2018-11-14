from docutils.parsers.rst import directives
from sphinx.directives.code import CodeBlock

from flake8_rst.sourceblock import ROLES as SOURCEBLOCK_ROLES
from flake8_rst.checker import ROLES as CHECKER_ROLES

try:
    from IPython.sphinxext.ipython_directive import IPythonDirective
except ImportError:
    IPythonDirective = None


def add_custom_roles(directive_class):
    """

    :type directive_class: Type[Directive]
    """
    if not directive_class:
        return
    for role in SOURCEBLOCK_ROLES + CHECKER_ROLES:
        directive_class.option_spec['flake8-' + role] = directives.unchanged


def setup(app):
    add_custom_roles(CodeBlock)
    add_custom_roles(IPythonDirective)
