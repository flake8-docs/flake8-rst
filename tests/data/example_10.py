"""
Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia
deserunt mollit anim id est laborum.

>>> # extract 100 LDA topics, using default parameters
>>> lda = LdaModel(corpus=mm, id2word=id2word, num_topics=100, distributed=True)

Allow non code between blocks of code
and also allow wrapping with ...

>>> # extract 100 LDA topics, using default parameters
>>> lda = LdfModel(corpus=cm, id2word=id2word,
...                num_topics=100, distributed=lda)

Only check for code, not results:

>>> print('This line is highlighted.')
This line is highlighted.
"""
