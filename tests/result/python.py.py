# line number: 13
# indent: 8
data_table = Table('data_table', metadata,
    Column('id', Integer, primary_key=True),
    Column('data', JSONB)
)

with engine.connect() as conn:
    conn.execute(
        data_table.insert(),
        data = {"key1": "value1", "key2": "value2"}
    )
# end of block

