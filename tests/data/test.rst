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

.. sourcecode:: python

    Table("mytable", meta,
          Column("somecolumn", Integer, default=12)
          )

If we want the sequence to be used as a server-side default,
meaning it takes place even if we emit INSERT commands to the table from
the SQL command line, we can use the :paramref:`.Column.server_default`
parameter in conjunction with the value-generation function of the
sequence, available from the :meth:`.Sequence.next_value` method.  Below
we illustrate the same :class:`.Sequence` being associated with the
:class:`.Column` both as the Python-side default generator as well as
the server-side default generator

.. sourcecode:: python

    cart_id_seq = Sequence('cart_id_seq', metadata=meta)
    table = Table("cartitems", meta,
                  Column(
                      "cart_id", Integer, cart_id_seq,
                      server_default=cart_id_seq.next_value(), primary_key=True),
                  Column("description", String(40)),
                  Column("createdate", DateTime())
                  )

or with the ORM

.. sourcecode:: python

    class CartItem(Base):
        __tablename__ = 'cartitems'

        cart_id_seq = Sequence('cart_id_seq', metadata=Base.metadata)
        cart_id = Column(
            Integer, cart_id_seq,
            server_default=cart_id_seq.next_value(), primary_key=True)
        description = Column(String(40))
        createdate = Column(DateTime)

When the "CREATE TABLE" statement is emitted, on PostgreSQL it would be
