import sys

import pytest
from collections import OrderedDict

from flake8_rst.application import convert_default_groupnames


@pytest.mark.parametrize('value, expected', [
    ('*-*: default', OrderedDict(A=OrderedDict(A='default'))),
    ('rst-ipython: default, py-code-block: default', OrderedDict(rst=OrderedDict(ipython='default'),
                                                                 py=OrderedDict(code_block='default'))),
    ('rst-ipython: default\nrst-code-block: default', OrderedDict(rst=OrderedDict(ipython='default',
                                                                                  code_block='default'))),
    ('rst-ipy*: default, # Ignored Comment\npy-code-block: default',
     OrderedDict(rst=OrderedDict(ipyA='default'), py=OrderedDict(code_block='default'))),
])
@pytest.mark.skipif(sys.version_info < (3, 3), reason="python2 scrambles expected order of dictionary items")
def test_convert_default_groupnames(value, expected):
    result = convert_default_groupnames(value)

    def convert_expected(dictionary):
        altered_dict = OrderedDict()

        for key, value in dictionary.items():
            key = key.replace('A', '*').replace('_', '-')
            altered_dict[key] = convert_expected(value) if isinstance(value, dict) else value

        return altered_dict

    assert convert_expected(expected) == result
