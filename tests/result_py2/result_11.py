('test_precisely',
 [('E111', 16, 15, 'indentation is not a multiple of four', u'      ....:    print(a[i] is b[i])\n'),
  (u'E231', 11, 29, u"missing whitespace after ','", u'   In [10]: %timeit a = (1, 2,name)  # noqa: F821\n'),
  ('F821', 9, 19, "undefined name 'brian'", u'   In [9]: other = brian\n'),
  ('W391', 17, 11, 'blank line at end of file', u'      ....:\n')],
 {'logical lines': 6, 'physical lines': 7, 'tokens': 53})
