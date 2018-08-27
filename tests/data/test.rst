.. _metadata_constraints_toplevel:
.. _metadata_constraints:

.. module:: sqlalchemy.schema

================================
Defining Constraints and Indexes
================================

This section will discuss SQL :term:`constraints` and indexes.  In SQLAlchemy
the key classes include :class:`.ForeignKeyConstraint` and :class:`.Index`.

.. _metadata_foreignkeys:

Defining Foreign Keys
---------------------

In SQLAlchemy as well as in DDL, foreign key constraints can be defined as
additional attributes within the table clause, or for single-column foreign
keys they may optionally be specified within the definition of a single
column. The single column foreign key is more common, and at the column level
is specified by constructing a :class:`~sqlalchemy.schema.ForeignKey` object
as an argument to a :class:`~sqlalchemy.schema.Column` object

.. sourcecode:: python

    user_preference = Table('user_preference', metadata,
        Column('pref_id', Integer, primary_key=True),
        Column('user_id', Integer, ForeignKey("user.user_id"), nullable=False),
        Column('pref_name', String(40), nullable=False),
        Column('pref_value', String(100))
    )

Above, we define a new table ``user_preference`` for which each row must
contain a value in the ``user_id`` column that also exists in the ``user``
table's ``user_id`` column.
