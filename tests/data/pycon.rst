Running LDA
____________

Run LDA like you normally would, but turn on the `distributed=True` constructor
parameter:

.. sourcecode:: pycon

    >>> # extract 100 LDA topics, using default parameters
    >>> lda = LdaModel(corpus=mm, id2word=id2word, num_topics=100, distributed=True)

    using distributed version with 4 workers
    running online LDA training, 100 topics, 1 passes over the supplied corpus of 3199665 documets,
    updating model once every 40000 documents
    ..

Some another text
