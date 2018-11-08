('test_precisely',
 [('E111', 12, 15, 'indentation is not a multiple of four',
   '               print(a[i] is b[i])\n'),
  ('F821', 8, 20, "undefined name 'brian'",
   '            other = brian\n')],
 {'logical lines': 8, 'physical lines': 8, 'tokens': 55})
