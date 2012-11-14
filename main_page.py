import lxml.html
from bs4 import BeautifulSoup
import sys
import urllib2
import re
from urlparse import urljoin
from Queue import Queue, Empty
import threading
from store import URL , URLDictionary
from newforumpage import forumPage , connectChild
from dataBase import connectDB
import thread
from threading import Thread
from lxml import etree
from cStringIO import StringIO

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


if __name__ == "__main__":
    myhost = URL()
    myhost.setUrls("http://boards.baltimoreravens.com/")
    conn = connection(myhost.getUrls())
    conn.createConnection()
    parser = etree.HTMLParser()
    tree   = etree.parse(StringIO(conn.gethtmlPage()), parser)
    elements = tree.xpath('//title//text()')
    print elements
    
    urls = tree.xpath('.//td[@class="col_c_forum"]//h4//a/@href')
    #print urls
    p = re.compile('#')
    urlQ = []
    for url in urls:
        urlQ.append(url)
    forum = forumPage()
    nn = 0
    linkQ = Queue()
    dbs,cursor = connectDB()
    # 0,1 done 7,8 done
    for eachlink in urlQ[7:9]:
        #print eachlink
        linkQ = connectChild(eachlink)
        #while not linkQ.empty():
            #print linkQ.get()
        forum.connect(linkQ,cursor,True)
            
            
