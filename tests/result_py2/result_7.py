('test_precisely',
 [('E302', 31, 8, 'expected 2 blank lines, found 0', u'    >>> class EpochSaver(CallbackAny2Vec):\n'),
  ('E501',
   39,
   88,
   'line too long (90 > 80 characters)',
   u"    ...         output_path = get_tmpfile('{}_epoch{}.model'.format(self.path_prefix, self.epoch))\n")],
 {'logical lines': 11, 'physical lines': 13, 'tokens': 94})
