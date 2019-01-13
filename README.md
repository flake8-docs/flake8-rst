# flake8-rst module 
[![PyPI](https://img.shields.io/pypi/v/flake8-rst.svg)](https://pypi.org/project/flake8-rst/)
[![conda-forge](https://anaconda.org/conda-forge/flake8-rst/badges/version.svg)](https://anaconda.org/conda-forge/flake8-rst)
[![Build Status](https://travis-ci.org/kataev/flake8-rst.svg?branch=master)](https://travis-ci.org/kataev/flake8-rst)

Allows run flake8 on code snippets in docstrings or RST files.


## Idea

idea proposed by Mike Bayer on https://github.com/zzzeek/sqlalchemy/pull/362 

> That said, if there was some alternate form of "doctest" that could simply test a code example both for Python syntax, pep8 compliance (which would be AWESOME) as well as symbol consistency, that would be helpful. The tool could be configured with common imports and symbols significant to SQLAlchemy examples and be helpful as a basic sanity check for code examples. As it is, when writing new documentation I have to organize and run the code in a separate .py file to make sure it does the right thing. So this is a problem, just my experience with doctest in writing the tutorials has shown me what it's good at and where it's likely getting in the way.

Realization inspired by https://github.com/asottile/blacken-docs


## Usage
You can install tool from pip `pip install flake8-rst`.

Tool search `sourcecode`, `code-block` and `ipython` blocks, crop and run flake8 on it:

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
```commandline
flake8-rst --bootstrap "import test"
```

flake8-rst bootstraps code snippets with this code, useful for fix import errors.
Load configuration from `[flake8-rst]` ini sections, like flake8.

## Advanced Usage

Custom Roles
------------

In order to use custom roles of `flake8-rst` in documentation with `Sphinx`, extend sphinx with `flake8_rst.sphinxext.custom_roles` in `conf.py`.
The roles have no effect on the generated documentation.

```python
extensions = [...,
              'flake8_rst.sphinxext.custom_roles'
              ]
```

| role                  |                                                  | example                                    | 
|-----------------------|--------------------------------------------------|--------------------------------------------|
| `:flake8-group:`      | Blocks with same group are combined to one.      | `:flake8-group: Group1`                    |
|                       | Blocks with group `None` are checked individual. | `:flake8-group: None`                      |
|                       | Blocks with group `Ignore` are not checked.      | `:flake8-group: Ignore`                    |
| `:flake8-set-ignore:` | Overwrites ignore list for current block.        | `:flake8-set-ignore: F821, E999`           |
| `:flake8-add-ignore:` | Adds arguments to ignore list for current block. | `:flake8-add-ignore: E999`                 |
| `:flake8-set-select:` | Overwrites select list for current block.        | `:flake8-set-select: E, F`                 |
| `:flake8-add-select:` | Adds arguments to select list for current block. | `:flake8-add-select: C404`                 |
| `:flake8-bootstrap:`  | Overwrites `--bootstrap` for current block       | `:flake8-bootstrap: import os; import sys` |

Keep in mind: 
* Roles added to blocks within the same group (except group `None`) have no effect unless they appear in the first block.
* provided bootstrap-code will get split by `; ` into individual lines.
* `E999 SyntaxError: invalid syntax` causes `flake8` to skip `AST` tests. Keep mandatory `E999` issues in blocks with 
`:flake8-group: Ignore` to preserve full testing for the rest of the blocks.

Default block naming
--------------------
You can specify default groupnames for all directives individually:

```commandline
flake8-rst --default-groupnames '<file-pattern>-><directive>: <groupname>'
```

`file-pattern` and `directive` are matched by `Unix filename pattern matching` in the order of appearance.

The default is `*.rst->*: default`, so all blocks in `*.rst` files are merged, in 
other files they stay individual.

But it's also possible to merge only `ipython` directives in `*.rst` files and leave other directives 
treated individually: `"*.rst->ipython: default"`

Examples:

```commandline
flake8-rst --default-groupnames "*.rst->*: default"
```

```buildoutcfg
[flake8-rst]
default-groupnames =
    *.rst-*: default
    *.py-code-block: default
```

------------------------------------------------------------------------------------------------------------------------

Disconnected blocks don't know previous defined names:
 
```text
.. code-block:: python

    class Example(Base):
        pass

.. code-block:: python
    
    import datetime
    
    obj = Example(datetime.datetime.now())            # F821 undefined name 'Example'
    
```

Once blocks are connected, different issues are found:

```text
.. code-block:: python
    :flake8-group: ExampleGroup
    
    class Example(Base):
        pass

.. code-block:: python
    :flake8-group: ExampleGroup
    
    import datetime                                   # E402 module level import not at top of file
    
    obj = Example(datetime.datetime.now())
    
```

If appropriate, issues can be ignored for a specific group:

```text


.. code-block:: python
    :flake8-group: ExampleGroup1
    :flake8-set-ignore: E402
    
    class Example(Base):
        pass

.. code-block:: python
    :flake8-group: ExampleGroup1
    
    import datetime
    
    obj = Example(datetime.datetime.now())



.. code-block:: python
    :flake8-group: ExampleGroup2
    
    class Example(Base):
        pass

.. code-block:: python
    :flake8-group: ExampleGroup2
    :flake8-set-ignore: E402                          # no effect, because it's not defined in first 
                                                      # block of ExampleGroup2 
        
    import datetime                                   # E402 module level import not at top of file
    
    obj = Example(datetime.datetime.now())
    
    
```

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
