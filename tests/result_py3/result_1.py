('test_precisely',
 [('F821', 7, 14, "undefined name 'LdaModel'",
   '        lda = LdaModel(corpus=mm, id2word=id2word, num_topics=100, distributed=True)\n'),
  ('F821', 7, 30, "undefined name 'mm'",
   '        lda = LdaModel(corpus=mm, id2word=id2word, num_topics=100, distributed=True)\n'),
  ('F821', 7, 42, "undefined name 'id2word'",
   '        lda = LdaModel(corpus=mm, id2word=id2word, num_topics=100, distributed=True)\n')],
 {'logical lines': 2, 'physical lines': 2, 'tokens': 23})
