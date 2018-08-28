# flake8-rst module
Allows run flake8 on code snippets in docstrings or RST files.


## Idea

idea proposed by Mike Bayer on https://github.com/zzzeek/sqlalchemy/pull/362 

> That said, if there was some alternate form of "doctest" that could simply test a code example both for Python syntax, pep8 compliance (which would be AWESOME) as well as symbol consistency, that would be helpful. The tool could be configured with common imports and symbols significant to SQLAlchemy examples and be helpful as a basic sanity check for code examples. As it is, when writing new documentation I have to organize and run the code in a separate .py file to make sure it does the right thing. So this is a problem, just my experience with doctest in writing the tutorials has shown me what it's good at and where it's likely getting in the way.

Realization inspired by https://github.com/asottile/blacken-docs


## Usage
Tool search `sourcecode` and `code-block` blocks, crop and run flake8 on it:

```text
.. sourcecode:: python

    class Example(Base):
        pass
```
or

```text
.. code-block:: python

    class Example(Base):
        pass
```

Supporting all flake8 arguments and flags except jobs (temporary), with additional one:
```text
flake8-rst --bootstrap "import test"
```

flake8-rst bootstraps code snippets with this code, useful for fix import errors.
Load configuration from `[flake8-rst]` ini sections, like flake8.

## Example

```text
d.kataev:flake8-rst§ flake8-rst --filename="*.py *.rst" tests/data/* --bootstrap="from sqlalchemy import Table, Column, Sequence, Integer, ForeignKey, String, DateTime"
tests/data/test.py:14:42: F821 undefined name 'metadata'
tests/data/test.py:15:13: E128 continuation line under-indented for visual indent
tests/data/test.py:16:28: F821 undefined name 'JSONB'
tests/data/test.py:19:14: F821 undefined name 'engine'
tests/data/test.py:22:21: E251 unexpected spaces around keyword / parameter equals
tests/data/test.py:22:23: E251 unexpected spaces around keyword / parameter equals
tests/data/test.rst:27:48: F821 undefined name 'metadata'
tests/data/test.rst:41:22: F821 undefined name 'meta'
tests/data/test.rst:56:52: F821 undefined name 'meta'
tests/data/test.rst:57:32: F821 undefined name 'meta'
tests/data/test.rst:69:20: F821 undefined name 'Base'
tests/data/test.rst:72:56: F821 undefined name 'Base'
```
