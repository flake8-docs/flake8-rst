class JSONB:
    """Represent the PostgreSQL JSONB type.

    The :class:`.JSONB` type stores arbitrary JSONB format data, e.g.:

    .. sourcecode:: python

        data_table = Table('data_table', metadata,
            Column('id', Integer, primary_key=True),
            Column('data', JSONB)
        )

        with engine.connect() as conn:
            conn.execute(
                data_table.insert(),
                data = {"key1": "value1", "key2": "value2"}
            )

    The :class:`.JSONB` type includ
    """
