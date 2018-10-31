Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia
deserunt mollit anim id est laborum.

>>> # extract 100 LDA topics, using default parameters
>>> lda = LdaModel(corpus=mm, id2word=id2word,
...                num_topics=100, distributed=distribution_required)
Intermediate output
>>> # extract 100 LDA topics, using default parameters
>>> ldb = LdbModel(corpus=mm, id2word=id2word, num_topics=100, distributed=True)
Final output

Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia
deserunt mollit anim id est laborum.