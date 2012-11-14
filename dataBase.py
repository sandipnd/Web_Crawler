import MySQLdb
import sys, traceback


def getTitleId(cursor,title):
    try:
        val = cursor.execute("select id from title where title=%s",title)
        return val
    except MySQLdb.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1])    

def databaseId(db):
    databaseId.id = db

def getdbId():
    return databaseId.id
def connectDB():
    global db
    try:
        db =  MySQLdb.connect(host="localhost",user="root",passwd="test123",db="project")
        cursor = db.cursor()
        databaseId(db)
        return db,cursor
    except MySQLdb.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1])
        sys.exit(0)
    
