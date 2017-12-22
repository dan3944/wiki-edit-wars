import pymysql
import requests
from html.parser import HTMLParser
from final import *

class ArticleParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.text = ''

    def handle_data(self, data):
        self.text += data


class ReferencesParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.isReferences = False
        self.references = []
        self.currentRef = ''
        self.olAmt = 0

    def handle_starttag(self, tag, attrs):
        for attr in attrs:
            if attr == ('class', 'references') and tag == 'ol':
                self.isReferences = True
                self.olAmt = 1


    def handle_endtag(self, tag):
        if self.isReferences:
            if tag == 'li':
                self.references.append(self.currentRef)
                self.currentRef = ''
            elif tag == 'ol':
                self.olAmt -= 1
                if self.olAmt == 0:
                    self.isReferences = False

    def handle_data(self, data):
        if self.isReferences:
            self.currentRef += data


def processArticleContents(articleID):
    articleID = articleID['id']
    print(articleID)
    json = queryAPI(pageids=articleID, prop='extracts')
    
    parser = ArticleParser()
    parser.feed(json['query']['pages'][str(articleID)]['title'])
    
    try:
        db = connectDB()
        execute(db, 'insert into article values (%s, %s, %s, %s, %s)', (
                        articleID,
                        parser.text,
                        json['query']['pages'][str(articleID)]['extract'],
                        None,
                        None ))

        processRevisions(articleID, db)
    
    except Exception as e:
        print('%s: %s' % (e, articleID))

    db.close()


def processRevisions(articleID, db=None):
    print(articleID)
    json = { 'continue' : { 'rvcontinue' : None } }
    revs = []

    while 'continue' in json:
        rvcont = json['continue']['rvcontinue']
        json = queryAPI(pageids=articleID, prop='revisions', rvprop='timestamp|ids|userid|sha1', rvlimit=500, rvcontinue=rvcont)
        revs += json['query']['pages'][str(articleID)]['revisions']

    try:
        sql = 'insert into revision values' + ','.join("\n(%s, %s, '%s', %s, %s, '%s')" % (
                rev['revid'],
                articleID,
                rev['timestamp'].replace('T', ' ').replace('Z', ''),
                rev.get('userid') or 'null',
                int('anon' in rev),
                rev.get('sha1') or 'null'
            ) for rev in revs)

        db = db or connectDB()
        execute(db, sql)

    except KeyError as e:
        print(articleID, e)

def saveRandomArticles(amt):
    articles = []
    cont = None

    while len(articles) < amt:
        json = queryAPI(list='random', rnlimit=amt - len(articles), rnnamespace=0, rncontinue=cont)
        cont = json['continue']['rncontinue']
        articles += json['query']['random']

    parallel(processArticleContents, articles)


def saveRevisions():
    db = connectDB()
    rows = [ row['id'] for row in query(db, 'select id from article') ]
    parallel(processRevisions, rows, threads=50)

def saveNumRefs(articleID):
    print(articleID)
    html = requests.get('http://en.wikipedia.org/?curid=%s' % articleID).text
    parser = ReferencesParser()
    parser.feed(html)
    refs = len(parser.references)
    db = connectDB()
    execute(db, 'update article set num_refs = %s where id = %s', (refs, articleID))

def saveAllNumRefs():
    db = connectDB()
    articleIDs = [ row['id'] for row in query(db, 'select id from article where num_refs is null') ]
    parallel(saveNumRefs, articleIDs)


if __name__ == '__main__':
    saveAllNumRefs()
