import sklearn.naive_bayes as nbayes
import collections # for computing bag-of-words
import json # for loading bag-of-words
import pickle # for saving and loading the model
import random # for splitting training and test data
from final import *


def saveDataTable():
    db = connectDB()
    rows = query(db, 'select wordbag from article')
    articlesPerWord = collections.Counter()
    split = 0.8 # train/test split

    for i, row in enumerate(rows):
        if i % 1000 == 0: print(i)
        words = json.loads(row['wordbag']).keys()
        articlesPerWord.update(words)

    # already lemmatized and stopword-filtered
    vocab = [ word for word, count in articlesPerWord.items() if count > 10 ]
    rows = query(db, 'select id, controversy, wordbag, num_refs from article')
    
    # each row is an article
    # each column is a word
    # the value of a cell is the tf score of a word in a given article
    with open('train.csv', 'w') as fTrain, open('test.csv', 'w') as fTest:
        for i, row in enumerate(rows):
            if i % 100 == 0: print(i)
            wordbag = json.loads(row['wordbag'])
            totalCount = sum(wordbag.values())

            if totalCount == 0:
                tf = lambda word: '0'
            else:
                tf = lambda word: str(wordbag.get(word, 0) / totalCount)

            # id, controversy, wordcount, references per word
            articleInfo = '%s,%s,%s,%s,' % (row['id'], row['controversy'], totalCount, row['num_refs'] / (totalCount or 1))
            raw = articleInfo + ','.join(map(tf, vocab)) + '\n'

            if random.random() < split:
                fTrain.write(raw)
            else:
                fTest.write(raw)


def readDataTable(fileName):
    with open(fileName) as f:
        for line in f:
            row = line.split(',')
            yield (int(row[0]), int(row[1]), # id, controversy, feature values...
                    list(map(float, row[2:])))

def trainNaiveBayes(csvFile, model):
    batchSize = 1000
    xBatch, yBatch = [], []

    for i, (articleID, controversy, values) in enumerate(readDataTable(csvFile)):
        if i % 100 == 0: print(i)
        # values = list(map(bool, values)) # uncomment this when using Bernoulli Naive Bayes
        xBatch.append(values)
        yBatch.append(controversy > 0)

        if len(xBatch) == batchSize:
            print('Fitting...')
            model.partial_fit(xBatch, yBatch, classes=[True, False])
            xBatch, yBatch = [], []

    with open('model.pkl', 'wb') as f:
        pickle.dump(model, f)


def evalNaiveBayes(csvFile):
    truePos  = 0
    trueNeg  = 0
    falsePos = 0
    falseNeg = 0

    with open('model.pkl', 'rb') as f:
        model = pickle.load(f)

        for i, (articleID, controversy, values) in enumerate(readDataTable(csvFile)):
            if i % 100 == 0: print(i)
            actual = controversy > 0
            # values = list(map(bool, values)) # uncomment this when using Bernoulli Naive Bayes
            predicted = model.predict([values])[0]

            if       actual and     predicted: truePos  += 1
            elif     actual and not predicted: falseNeg += 1
            elif not actual and     predicted: falsePos += 1
            elif not actual and not predicted: trueNeg  += 1

    print('''    
    Actual/Predicted    | True | False
                        --------------
                True    | %s | %s
                False   | %s | %s ''' % (truePos, falseNeg, falsePos, trueNeg))

    print('%% True  correct: %s' % (truePos / (truePos + falseNeg)))
    print('%% False correct: %s' % (trueNeg / (trueNeg + falsePos)))
    print('Accuracy: %s' % ((truePos + trueNeg) / (truePos + trueNeg + falsePos + falseNeg)))


if __name__ == '__main__':
    saveDataTable()
    trainNaiveBayes('train.csv', model=nbayes.MultinomialNB())
    evalNaiveBayes('test.csv')
