import collections
from final import *

def calcControversy(articleID):
    articleID = articleID['id']
    db = connectDB()
    revisions = list(query(db, '''
                select user, hash
                from revision
                where article_id = %s
                order by createdat desc
            ''',
            (articleID,)))

    encountered = set()
    reverts = set()

    # identify revisions that are reverts
    for row in revisions:
        if row['hash'] in encountered:
            reverts.add(row['hash'])
        else:
            encountered.add(row['hash'])

    # identify reverter/revertee
    revertPairs = set()
    for row, prevRow in zip(revisions, revisions[1:]):
        if row['hash'] in reverts and row['hash']:
            reverter = row['user']
            revertee = prevRow['user']
            revertPairs.add((reverter, revertee))

    # identify mutual reverting pairs
    mutualReverters = set()
    for reverter, revertee in revertPairs:
        switch = revertee, reverter
        if switch in revertPairs and switch not in mutualReverters:
            mutualReverters.add((reverter, revertee))

    # get weights of users
    userWeights = collections.Counter(rev['user'] for rev in revisions)

    # get weights of mutually reverting pairs
    revPairWeights = [ min(userWeights[u1], userWeights[u2]) for u1, u2 in mutualReverters ]

    # calculate total controversialness
    controversy = len(userWeights) * (sum(revPairWeights) - max(revPairWeights or [0]))
    print('%s:  %s' % (articleID, controversy))

    execute(db, 'update article set controversy = %s where id = %s',
            (controversy, articleID))

    db.close()


def calcAllArticles():
    db = connectDB()
    articleIDs = query(db, 'select id from article where controversy is null')
    parallel(calcControversy, articleIDs)


if __name__ == '__main__':
    calcAllArticles()
