
from collections import deque
import Queue

class URL:
    def __init__(self):
        self.urlQueue = deque([])
    def setUrls(self,urlString):
        self.urlQueue.append(urlString)
    def  getUrls(self):
        if len(self.urlQueue) > 0:
            return self.urlQueue.popleft()

#x= URL()
#x.setUrls("abc")
#print x.getUrls()       

# we will store internal web pages here 

class URLDictionary:
    def __init__(self,urlList):
        self.urlDictionary = {}
        for urls in urlList:
            self.urlDictionary[urls] = Queue.Queue()
            
    def setUrls(self,parentUrl , childUrlQ):
        tempQ = Queue.Queue()
        tempQ = childUrlQ
        self.urlDictionary[parentUrl] = tempQ
    def getUrls(self,parentUrl):
         if self.urlDictionary.has_key(parentUrl):
             return self.urlDictionary[parentUrl]
         return ""   
    def getUrlDictKeys(self):
        return self.urlDictionary.keys()
