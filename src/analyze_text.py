import nltk.tokenize as tkn
import nltk.corpus as corpus
import nltk.stem.wordnet as wordnet
import collections
import json
from final import *


def fillWordBags():
    stopWords = set(corpus.stopwords.words('english'))
    lmtzr = wordnet.WordNetLemmatizer()
    db = connectDB()
    rows = query(db, 'select id, content from article where wordbag is null')
    sql = ''

    for i, row in enumerate(rows):
        wordbag = collections.Counter(
                lmtzr.lemmatize(word).lower()
                for word in tkn.word_tokenize(row['content'])
                if word.isalnum() and word.lower() not in stopWords
            )

        sql += "update article set wordbag = '%s' where id = %s;\n" \
                % (json.dumps(wordbag), row['id'])

        if i % 100 == 0:
            print(i)
            execute(db, sql)
            sql = ''

    execute(db, sql)


if __name__ == '__main__':
    fillWordBags()