('test_precisely',
 [('F821', 48, 13, "undefined name 'boto3'", u"    client = boto3.client('s3', 'us-west-2')\n"),
  ('F821', 49, 15, "undefined name 'S3Transfer'", u'    transfer = S3Transfer(client)\n')],
 {'logical lines': 6, 'physical lines': 7, 'tokens': 45})
