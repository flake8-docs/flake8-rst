('test_precisely',
 [('E111', 16, 15, 'indentation is not a multiple of four', '      ....:    print(a[i] is b[i])\n'),
  ('E231', 11, 29, "missing whitespace after ','", '   In [10]: %timeit a = (1, 2,name)  # noqa: F821\n'),
  ('F821', 9, 19, "undefined name 'brian'", '   In [9]: other = brian\n'),
  ('W391', 17, 11, 'blank line at end of file', '      ....:\n')],
 {'logical lines': 6, 'physical lines': 7, 'tokens': 53})
