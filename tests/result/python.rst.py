# line number: 26
# indent: 4
user_preference = Table('user_preference', metadata,
                        Column('pref_id', Integer, primary_key=True),
                        Column('user_id', Integer, ForeignKey("user.user_id"),
                               nullable=False),
                        Column('pref_name', String(40), nullable=False),
                        Column('pref_value', String(100))
                        )
# end of block

# line number: 40
# indent: 4
Table("mytable", meta,
      Column("somecolumn", Integer, default=12)
      )
# end of block

# line number: 55
# indent: 4
cart_id_seq = Sequence('cart_id_seq', metadata=meta)
table = Table("cartitems", meta,
              Column(
                  "cart_id", Integer, cart_id_seq,
                  server_default=cart_id_seq.next_value(), primary_key=True),
              Column("description", String(40)),
              Column("createdate", DateTime())
              )
# end of block

# line number: 68
# indent: 4
class CartItem(Base):
    __tablename__ = 'cartitems'

    cart_id_seq = Sequence('cart_id_seq', metadata=Base.metadata)
    cart_id = Column(
        Integer, cart_id_seq,
        server_default=cart_id_seq.next_value(), primary_key=True)
    description = Column(String(40))
    createdate = Column(DateTime)
# end of block

