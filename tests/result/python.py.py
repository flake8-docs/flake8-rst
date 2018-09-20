# line number: 24
# indent: 4
from gensim.models import AuthorTopicModel
from gensim.corpora import mmcorpus
from gensim.test.utils import common_dictionary, datapath, temporary_file
author2doc = {
    'john': [0, 1, 2, 3, 4, 5, 6],
    'jane': [2, 3, 4, 5, 6, 7, 8],
    'jack': [0, 2, 4, 6, 8]
}

corpus = mmcorpus.MmCorpus(datapath('testcorpus.mm'))

with temporary_file("serialized") as s_path:
    model = AuthorTopicModel(
         corpus, author2doc=author2doc, id2word=common_dictionary, num_topics=4,
         serialized=True, serialization_path=s_path
    )

    model.update(corpus, author2doc)  # update the author-topic model with additional documents

# construct vectors for authors
author_vecs = [model.get_author_topics(author) for author in model.id2author.values()]
# end of block

# line number: 59
# indent: 8
data_table = Table('data_table', metadata,
    Column('id', Integer, primary_key=True),
    Column('data', JSONB)
)

with engine.connect() as conn:
    conn.execute(
        data_table.insert(),
        data = {"key1": "value1", "key2": "value2"}
    )
# end of block

