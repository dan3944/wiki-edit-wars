import requests
import pymysql
import pprint
import multiprocessing

# this file contains various utility functions that I use in the rest of the code

ppr = pprint.PrettyPrinter().pprint


def parallel(func, vals, threads=20):
    return multiprocessing.Pool(threads).map(func, vals)

def queryAPI(**params):
    params['action'] = 'query'
    params['format'] = 'json'
    return requests.get('https://en.wikipedia.org/w/api.php', params=params).json()

def connectDB(dbName = 'edit_wars'):
    return pymysql.connect(
            host = 'localhost',
            user = 'root',
            password = 'pass',
            db = dbName,
            charset = 'utf8',
            cursorclass = pymysql.cursors.DictCursor
        )

def execute(db, sql, values=()):
    with db.cursor() as cursor:
        cursor.execute(sql, values)
    db.commit()

def query(db, sql, values=()):
    with db.cursor() as cursor:
        cursor.execute(sql, values)
        return cursor
