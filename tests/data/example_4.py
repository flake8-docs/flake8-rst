# SOME CODE

"""Author-topic model.

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

"""
