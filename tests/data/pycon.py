"""
Lorem ipsum dolor sit amet, consectetur adipiscing elit,
sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris
nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor
in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.
Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia
deserunt mollit anim id est laborum.

.. sourcecode:: pycon

    >>> # extract 100 LDA topics, using default parameters
    >>> lda = LdaModel(corpus=mm, id2word=id2word, num_topics=100, distributed=True)

    using distributed version with 4 workers
    running online LDA training, 100 topics, 1 passes over the supplied corpus of 3199665 documets
    updating model once every 40000 documents
    ..

Some another text
"""


class Test:
    """
    Lorem ipsum dolor sit amet, consectetur adipiscing elit,
    sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
    Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris
    nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor
    in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.
    Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia
    deserunt mollit anim id est laborum.

    .. sourcecode:: pycon

        >>> # extract 100 LDA topics, using default parameters
        >>> lda = LdaModel(corpus=mm, id2word=id2word, num_topics=100, distributed=True)

    using distributed version with 4 workers
    running online LDA training, 100 topics, 1 passes over the supplied corpus of 3199665 documets,
    updating model once every 40000 documents
        ..

    Some another text
    """

    some_field = 1

    def test(self):
        """
        Lorem ipsum dolor sit amet, consectetur adipiscing elit,
        sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
        Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris
        nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor
        in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.
        Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia
        deserunt mollit anim id est laborum.

        .. sourcecode:: pycon

            >>> # extract 100 LDA topics, using default parameters
            >>> lda = LdaModel(corpus=mm, id2word=id2word, num_topics=100, distributed=True)

        using distributed version with 4 workers
        running online LDA training, 100 topics, 1 passes over the supplied corpus of 3199665 documets,
        updating model once every 40000 documents
        ..

        Some another text
        """

        return 1
