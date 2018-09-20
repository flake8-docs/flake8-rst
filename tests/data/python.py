# SOME CODE

"""Author-topic model.

This module trains the author-topic model on documents and corresponding author-document dictionaries.
The training is online and is constant in memory w.r.t. the number of documents.
The model is *not* constant in memory w.r.t. the number of authors.

The model can be updated with additional documents after training has been completed. It is
also possible to continue training on the existing data.

The model is closely related to :class:`~gensim.models.ldamodel.LdaModel`.
The :class:`~gensim.models.atmodel.AuthorTopicModel` class inherits  :class:`~gensim.models.ldamodel.LdaModel`,
and its usage is thus similar.

The model was introduced by  `Rosen-Zvi and co-authors: "The Author-Topic Model for Authors and Documents"
<https://arxiv.org/abs/1207.4169>`_. The model correlates the authorship information with the topics to give a better
insight on the subject knowledge of an author.

Example
-------

.. sourcecode:: pycon

    >>> from gensim.models import AuthorTopicModel
    >>> from gensim.corpora import mmcorpus
    >>> from gensim.test.utils import common_dictionary, datapath, temporary_file

    >>> author2doc = {
    ...     'john': [0, 1, 2, 3, 4, 5, 6],
    ...     'jane': [2, 3, 4, 5, 6, 7, 8],
    ...     'jack': [0, 2, 4, 6, 8]
    ... }
    >>>
    >>> corpus = mmcorpus.MmCorpus(datapath('testcorpus.mm'))
    >>>
    >>> with temporary_file("serialized") as s_path:
    ...     model = AuthorTopicModel(
    ...          corpus, author2doc=author2doc, id2word=common_dictionary, num_topics=4,
    ...          serialized=True, serialization_path=s_path
    ...     )
    ...
    ...     model.update(corpus, author2doc)  # update the author-topic model with additional documents
    >>>
    >>> # construct vectors for authors
    >>> author_vecs = [model.get_author_topics(author) for author in model.id2author.values()]

"""

from __future__ import absolute_import


class JSONB:
    """Represent the PostgreSQL JSONB type.

    The :class:`.JSONB` type stores arbitrary JSONB format data, e.g.:

    .. sourcecode:: python

        data_table = Table('data_table', metadata,
            Column('id', Integer, primary_key=True),
            Column('data', JSONB)
        )

        with engine.connect() as conn:
            conn.execute(
                data_table.insert(),
                data = {"key1": "value1", "key2": "value2"}
            )

    The :class:`.JSONB` type includ
    """
