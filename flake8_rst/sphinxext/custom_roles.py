from docutils.parsers.rst import directives
from sphinx.directives.code import CodeBlock

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
    directive_class.option_spec['flake8-group'] = directives.unchanged


def setup(app):
    add_custom_roles(CodeBlock)
    add_custom_roles(IPythonDirective)
