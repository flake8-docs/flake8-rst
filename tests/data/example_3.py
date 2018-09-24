class Test:

    some_field = 1

    def test(self):
        """
        Lorem ipsum dolor sit amet, consectetur adipiscing elit,
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
