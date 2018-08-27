import textwrap

from flake8_rst.rst import find_sourcecode


def test_find():
    with open('tests/data/test.rst') as fd:
        with open('tests/data/test.rst') as fd2:
            for code, indent, start, end in find_sourcecode(fd.read()):
                fd2.seek(start)
                data = fd2.read(end - start)
                data = textwrap.dedent(data)
                assert data == code
