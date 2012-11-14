from bs4 import BeautifulSoup
import sys
import urllib2
import re
from urlparse import urljoin
import Queue
import re
from calculateDate import todays , yesterdays , processForDatabase , nMinutesAgo
import itertools
import MySQLdb
import unicodedata
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
from lxml import etree
from cStringIO import StringIO
import lxml.html as lh
#from lxml.html import soupparser

class forumPage:
    def __init__(self):
        self.users = []
        self.times = []
        self.comments = []
        self.title=""
        self.titleId = 0
        
    def connect(self,urlQ,cursor,flag=False):
        while not urlQ.empty():
            
            url = urlQ.get()
            if url == "next":
                url = urlQ.get()
                nextFLink = Queue.Queue()
                nextFLink = connectChild(url)
                #print "nextF" , nextFLink
                self.connect(nextFLink,cursor)
            try:
                print url
                openConxn = urllib2.Request(url)
                response = urllib2.urlopen(openConxn)
                #print response.read()
                htmlx = response.read()
                #print html
                parser   = etree.HTMLParser()  
		soup = BeautifulSoup(htmlx)        
            except Exception as e:
                print e
                return            
            tree = etree.parse(StringIO(htmlx), parser)
            #doc = html.fromstring(htmlx)
            #self.getsubForum(tree,)
            self.getTitle(tree)        
            self.getContent(soup)
            self.getUsers(tree)
            self.getTime(tree)
            self.addToDatabase(cursor)
            nextLink = self.getNextLink(tree)#subtopic link
            if len(nextLink) > 0:
                tlinkQ = Queue.Queue()
                sublink = nextLink[0] 
                tlinkQ.put(sublink)
                self.connect(tlinkQ,cursor)
    def addToDatabase(self,cursor):
        for t,u,c in itertools.izip(self.times,self.users,self.comments):
            sql = ("""INSERT INTO ravens(title,users,post_time,message) VALUES (%s,%s,%s,%s)""", (self.title,u.encode('ascii','replace'),t,c.encode('ascii','replace')))
            try:
               #pass
               cursor.execute(*sql)
            except IndexError:
               pass
            except TypeError:
               pass
            except MySQLdb.Error, e:
                print "Error %d: %s" % (e.args[0], e.args[1])
                pass
            
    def getsubForum(self,tree):
        myurls = tree.xpath('.//h3[@class="nodeTitle"]//a/@href')
        if len(myurls) == 0:
            return
        urlQ = []
        for urls in myurls:
            if url.find('#') < 0:
                url = parent + url
                #print url
                urlQ.append(url)
        linkQ = Queue.Queue()
        for eachlink in urlQ:
            linkQ = connectChild(eachlink)
            self.connect(linkQ,True)
                    
    def getNextLink(self,tree):
        link = tree.xpath('.//link[@rel="next"]/@href')
        return link
    def getTitle(self,tree):
        #title = tree.xpath('.//a[@class="PreviewTooltip"]/text()')
        #print title
        title = tree.xpath('.//title/text()')
        args = 0
        if len(title) > 0:
            self.title=title[0].encode('ascii','replace')
            args = 1
        print self.title    
    def getUsers(self,tree):
        self.users = []
        self.users = tree.xpath('.//div[@class="author_info"]//div/span//text()')
        #print "users"
        #print self.users

    def getContent(self,soup):
        self.comments = []
    	for div in soup.findAll('div',attrs={'class':'post_body'}):
		nextDiv =  div.findNext('div', attrs={'class':'post entry-content '})
		commnts = nextDiv.text
                #print "-----***********------------------"
		commnts = commnts.replace('\t','')
                commnts = commnts.replace('\n','')
                commnts = commnts.replace('\r','')
                #commnts.encode('ascii','ignore')
                commnts = commnts.replace('\u','')
                commnts = commnts.replace('\'','')
                #self.comments.append(nextDiv)
                self.comments.append(commnts)
    def getTime(self,tree):
        self.times = []
        mytimes = []
        mytimes = tree.xpath('.//div[@class="post_body"]//p//abbr/text()')
        #mytimes = tree.xpath('.//a[@title="Permalink"]//span[@class="DateTime"]/text()')
        for td in mytimes:
            #convert time format
            matchObjT = re.match( r'Today,', td, re.M|re.I)
            matchObjY = re.match( r'Yesterday,', td, re.M|re.I)
            matchObjD = re.search( r'minutes', td, re.M|re.I)
            matchA = re.search(r'A minute',td, re.M|re.I)
            if matchA :
                continue
            
            if matchObjT:
                td = todays(td)
            elif matchObjY:
                td = yesterdays(td)
            elif matchObjD:
                td = nMinutesAgo(td)
            else:
                td  = td.replace('-','')
            #print td    
            time_f = processForDatabase(td)
            #print time_f
            self.times.append(time_f)
        #print self.times

def connectChild(url):
    mylinks = Queue.Queue()
    #urlappend= "http://www.packerforum.com/"
    try:
        #print "in connectchild"
        print url
        openConxn = urllib2.Request(url)
        response = urllib2.urlopen(openConxn)
        #print response.read()
        html = response.read()
        #print html
        parser   = etree.HTMLParser()          
    except Exception as e:
        print e
        return            
    tree = etree.parse(StringIO(html), parser)
    tmplinks= tree.xpath('.//td[@class="col_f_content "]/h4//a/@href')
    #print tmplinks
    for ln in tmplinks:
        #ln = urlappend + ln
        mylinks.put(ln)
    link = tree.xpath('.//link[@rel="next"]/@href')
    if link != []:
        nlink = link[0]
        mylinks.put("next")
        mylinks.put(nlink)
    return mylinks
