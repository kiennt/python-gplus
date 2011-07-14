import socket
import threading
import Queue
import urllib2
import sys
import traceback
import time
from sets import Set

import cfg
import gplus_extracter
from nlp import VietnameseDetect as vd

class InputHandler(threading.Thread):
    def __init__(self, main):
        threading.Thread.__init__(self)
        self.main = main
        
    def run(self):
        print "Start listening from server"
        while True:
            try:
                data = self.main.socket.recv(cfg.BUF_SIZE)
                if data != "":                    
                    uids = data.split(',')
                    for uid in uids[:-1]: 
                        if len(uid) == 21:                       
                            #print "server request crawl ", uid
                            self.main.list_user_id.put(uid)
            except:
                print "Input handler exception "

class Downloader(threading.Thread):
    def __init__(self, main, did):        
        threading.Thread.__init__(self)
        self.id = did
        self.main = main
        
    def run(self):
        while True:
            uid = self.main.list_user_id.get()
            try:     
                proxy = self.main.get_next_proxy()
                print "Begin crawl", uid, "with proxy", proxy
                extracter = gplus_extracter.GplusExtracter(self.main, uid, proxy)                           
                # get user friends and follows
                friend_info = extracter.get_friends_info()  
                # get user info
                user_info = extracter.get_user_info()                                              
                # send user info to server    
                print "Send user info", uid, " to server", user_info
                self.main.lock.acquire()            
                self.main.socket.send('[' + user_info + ']')   
                self.main.lock.release()
                
                # send list friend to server
                print "Send list friends of", uid, " to server"
                self.main.lock.acquire()            
                self.main.socket.send('[' + friend_info + ']')                                
                self.main.lock.release()
                
                self.main.list_user_id.task_done()
            except:
                print "Downloader", self.id, "exception"
                #traceback.print_exc(file=sys.stdout)
                self.main.list_user_id.put(uid)
                time.sleep(1)
                    
class CrawlerClient(object):
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.list_user_id = Queue.Queue()
        self.list_proxies = ['184.72.4.242:80',
                             '184.22.240.161:3128',
                             '184.22.240.160:3128',
                             '69.160.245.113:8888',
                             '201.65.237.214:8080',
                             '196.201.208.31:3128',
                             '210.212.20.164:3128',
                             '190.202.87.131:3128',
                             '61.7.241.18:3128',
                             '202.51.120.195:8080',
                             '217.219.69.122:8080',
                             '200.195.147.172:8080',
                             '189.22.152.3:3128',]
        self.current_proxy = 0
        self.lock = threading.Condition()
        self.vd = vd()

    def start(self):
        try:
            self.socket.connect((cfg.HOST, cfg.PORT))
            print "connect to server success"
            
            self.input = InputHandler(self)
            self.input.start()
                        
            for i in range(cfg.MAX_THREAD_PER_CLIENT):
                downloader = Downloader(self, i)
                downloader.start()
        except socket.error, e:
            print "could not connect to server"
            print e
            sys.exit(1)
    
    def get_next_proxy(self):
        self.lock.acquire()
        num_proxies = len(self.list_proxies)
        if num_proxies == 0 or num_proxies < self.current_proxy:
            return None         
        proxy = self.list_proxies[self.current_proxy]        
        self.current_proxy = self.current_proxy + 1
        if self.current_proxy == num_proxies:
            self.current_proxy = 0
        self.lock.release()
        return proxy
            
def main():
    crawler = CrawlerClient()
    crawler.start()
    
if __name__ == "__main__":
    main()
