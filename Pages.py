from bs4 import BeautifulSoup
import sys
import urllib2
import re
from urlparse import urljoin
from Queue import Queue, Empty
import threading
from store import URL , URLDictionary
from forumpage import connectChild , forumPage
from dataBase import connectDB
import thread
from threading import Thread
import lxml.html

lock = threading.Lock()
def extractLink(hrefs):
    p = re.compile('<a href=\"(.*)\" title')
    #print type(hrefs)
    m = p.match(hrefs)
    if m == None:
        return None
    return m.group(1)

def crawlThread(links,childDict,dbs,cursor,forum,start,end):
    #global dbs
    global lock
    #print dbs
    dbs.commit()
    for eachLink in links[start:end]:
       print "each link" , eachLink
       forum.connect(childDict.getUrls(eachLink),cursor,True)
       lock.acquire()
       dbs.commit()
       lock.release()
       

class connection:
    def __init__(self,host):
        self.host = host
        self.htmlPage = ""
    def createConnection(self):
        try:
            openConxn = urllib2.Request(self.host)
            response = urllib2.urlopen(openConxn)
            self.htmlPage = response.read()
        except Exception as e:
            print e
            exit
    def gethtmlPage(self):
        return self.htmlPage
    def getHost(self):
        return self.host

    
class ParentWebPage:
    def __init__(self , connectionClass):
        self.content = {}
        self.hrefs = {}
        self.htmlPage = connectionClass.gethtmlPage()
        self.url = connectionClass.getHost()
        self.soup = BeautifulSoup(connectionClass.gethtmlPage())
        self.links = {}
    def getContent(self):
        if self.content.has_key(self.url):
            return self.content[self.url]
    def gethrefs(self):
        if self.hrefs.has_key(self.url):
            return self.hrefs[self.url]
    def setContent(self):
        self.content[self.url] = self.htmlPage
    def sethrefs(self):
        #self.hrefs[self.url] = self.soup.find_all('a')
        self.hrefs[self.url] = self.soup.find_all(href=re.compile("showforum"))
    def setLinks(self):
        templinks = []      
        for link in self.hrefs[self.url]:
            templinks.append(link.get('href'))
            #templinks.append(link)
        self.links[self.url] = templinks
    def getLinks(self):
        return self.links[self.url]
    
if __name__ == "__main__":
    #print sys.path
    #global dbs
    dbs,cursor = connectDB()
    myhost = URL()
    myhost.setUrls("http://seahawkshuddle.com/forum/")
    conn = connection(myhost.getUrls())
    conn.createConnection()
    #conn.gethtmlPage()
    myparent = ParentWebPage(conn)
    myparent.setContent()
    #print "content = ", myparent.getContent()
    tree= lxml.html.parse('http://seahawkshuddle.com/forum/')
    #print tree
    elements = tree.xpath('//title//text()')
    print elements
    myparent.sethrefs()
    myparent.setLinks()
    #print myparent.getLinks()
    #print type(myparent.gethrefs())
    childDict = URLDictionary(myparent.getLinks())
    linkQ = Queue()
    for eachLink in myparent.getLinks():
        linkQ = connectChild(eachLink)
        #print eachLink
        #while not linkQ.empty():
        #print linkQ.get()
        childDict.setUrls(eachLink,linkQ)
    forum = forumPage()
    lenlist = len(myparent.getLinks())
    lslice = lenlist / 2
    print myparent.getLinks()
    '''
    for eachLink in myparent.getLinks():
       print "each link" , eachLink
       forum.connect(childDict.getUrls(eachLink),cursor,True)
    '''   
    try:
        #thread.start_new_thread( crawlThread, (myparent.getLinks(),childDict,cursor,0,4,) )
        #thread.start_new_thread( crawlThread, (myparent.getLinks(),childDict,cursor,5,7,) )
        th1 = Thread(None,crawlThread,None,(myparent.getLinks(),childDict,dbs,cursor,forum,0,6))
        th2 = Thread(None,crawlThread,None,(myparent.getLinks(),childDict,dbs,cursor,forum,5,10))
        #th1.setDaemon(True)
        th1.start()
        #th2.start()
        th1.join()
        ##th2.join()
    except Exception as errtxt:
        print errtxt
        print "Error: unable to start thread"
  

