import socket
import threading
import Queue
import time
import sys
import traceback

import cfg
import model

class CrawlDispatcher(threading.Thread):
    """CrawlDispatcher took id need to crawl from a queue 
    and dispatch it to a crawl client
    """
        
    def __init__(self, server, seeds, sleep_time):
        """init function
        server: type CrawlerServer
        seeds: type list - initial id list
        """
        threading.Thread.__init__(self)
        self.server = server
        self.is_running = True
        self.sleep_time = sleep_time
        # init queue
        self.queue = Queue.Queue()
        #print("Begin with seeds", seeds)
        for seed in seeds:
            self.queue.put(seed)
            self.server.list_user[seed] = 1
            
    def run(self):
        while True:            
            if self.is_running:
                client = self.server.server.get_next_client()            
                if client is not None:
                    # get next id
                    uid = self.queue.get()                
                    # request client crawl uid
                    # print("Request client crawl ", uid)
                    client.send(uid + ",")
                    self.queue.task_done()
                    time.sleep(self.sleep_time)
                
    def pause(self):
        self.is_running = False
            
    def resume(self):
        self.is_running = True

class ClientHandler(threading.Thread):
    """ClientHandler listen and process request from a CrawlerClient
    Request is a message which has format:
       {MESSAGE_TYPE, ....}
    There are 2 types of message:
    1. USER_INFO message: client finish crawl user info, and it ask server to update user info
       {'1', user_id, user_name, friends, followers, user_pic, user_sex}
    2. USER_FRIENDS message: client took a friends list of user and ask server to crawl these user
       {'2', friend_id, friend_id, ....}
    """
    
    def __init__(self, server, socket, addr):
        """Init function
        server: type RequestHandler
        socket: type socket
        addr: type tuple which 0 is host name, and 1 is port of client
        """
        threading.Thread.__init__(self)
        self.server = server
        self.socket = socket
        self.addr = addr        
        
    def run(self):
        old_message = ""
        while True:
            try:
                data = self.socket.recv(cfg.BUF_SIZE)
                if data != "":
                    idx = data.find(']')
                    while idx > -1:
                        message = old_message + data[:idx+1]                        
                        arr = message[1:-1].split(',')
                        if arr[0] == cfg.MSG_USER_INFO and len(arr[1]) == 21:
                            self.server.server.db.insert_user_info(arr)
                            self.server.server.add_user_to_queue(arr[1])
                        elif arr[0] == cfg.MSG_LIST_USERS:
                            for uid in arr[1:]: 
                                if len(uid) == 21:
                                    self.server.server.add_user_to_queue(uid)
                        data = data[idx + 1:]
                        old_message = ""
                        idx = data.find(']')

                    old_message = old_message + data                          
            except:
                print "ClientHandler error from client ", self.addr[1]
                traceback.print_exc(file=sys.stdout)
    
class RequestHandler(threading.Thread):
    """RequestHandler is a thread to accept client
    With each client, RequestHandler will make a new ClientHandler to process
    client request
    """
    def __init__(self, server):
        """ Init function
        server: type CrawlerServer
        """
        threading.Thread.__init__(self)
        self.server = server
        # init conditon
        self.lock = threading.Condition()
        # list all client
        self.current_client = 0
        self.list_client = []
        try:
            print "Start server at", cfg.HOST, cfg.PORT
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)        
            self.socket.bind((cfg.HOST, cfg.PORT))
            self.socket.listen(cfg.MAX_CLIENT)
        except:
            print "Cannot create server socket"
            traceback.print_exc(file=sys.stdout)
            sys.exit(1)     
        
    def get_next_client(self):
        """Function: get_next_client: 
        Return next active client. 
        At this time, we just implement a round robin algorithm to dispatch request to crawler Client
        """
        self.lock.acquire()
        num_clients = len(self.list_client)
        if num_clients == 0 or num_clients < self.current_client:
            return None 
        # print("Client ", self.current_client)
        client = self.list_client[self.current_client]        
        self.current_client = self.current_client + 1
        if self.current_client == num_clients:
            self.current_client = 0
        self.lock.release()
        return client
    
    def run(self):
        while True:
            try:
                conn, addr = self.socket.accept()
                # add to list client
                print("Accept client from ", addr)
                self.list_client.append(conn)                
                # create new client hander
                client = ClientHandler(self, conn, addr)
                client.start()
            except:
                print "CrawlerServer RequestHandler exception"
                traceback.print_exc(file=sys.stdout)
    

class AdminClientHandler(threading.Thread):
    """AdminClientHandler to handler request from admin client
    """
    def __init__(self, admin_server, socket, addr):
        """Init function
        admin_server: type AdminServer
        socket: type socket
        addr: type Tuple, addr[0] is host name of client, addr[1] is port
        """
        threading.Thread.__init__(self)
        self.admin_server = admin_server
        self.socket = socket
        self.addr = addr
    
    def run(self):
        while True:
            try:                
                main = self.admin_server.server
                
                data = self.socket.recv(cfg.BUF_SIZE)
                if data in cfg.AdminMessage.COUNT_USER:
                    print "Admin ask about num of user in db"
                    uid_count = len(main.list_user.keys())
                    self.socket.send(str(uid_count))
                if data in cfg.AdminMessage.COUNT_CLIENT:
                    print "Admin ask num of client"
                    client_count = len(main.server.list_client)
                    self.socket.send(str(client_count))
                if data in cfg.AdminMessage.PAUSE_CRAWL_NEW:
                    main.new_users_handler.pause()
                    self.socket.send("pause new user crawler thread")
                if data in cfg.AdminMessage.PAUSE_CRAWL_OLD:
                    main.old_users_handler.pause()
                    self.socket.send("pause old user crawler thread")
                if data in cfg.AdminMessage.RESUME_CRAWL_NEW:
                    main.new_users_handler.resume()
                    self.socket.send("resume new user crawler thread")
                if data in cfg.AdminMessage.RESUME_CRAWL_OLD:
                    main.old_users_handler.resume()
                    self.socket.send("resume old user crawler thread")
                if data in cfg.AdminMessage.QUEUE_NEW:
                    count = main.new_users_handler.queue.qsize()
                    self.socket.send("new uids:" + str(count))
                if data in cfg.AdminMessage.QUEUE_OLD:
                    count = main.old_users_handler.queue.qsize()
                    self.socket.send("old uids:" + str(count))
                if data in cfg.AdminMessage.STATUS:
                    self.socket.send("new queue " + str(main.new_users_handler.is_running) + "\n" + "old queue" + str(main.old_users_handler.is_running))
            except:
                print "AdminClientHandler error from client ", self.addr[1]
                traceback.print_exc(file=sys.stdout)
                 
class AdminServer(threading.Thread):
    """AdminServer is server handler admin request
    AdminServer help we can see crawling process more detail
    """
    
    def __init__(self, server):
        """Init function
        server: type CrawlerServer
        """
        threading.Thread.__init__(self)
        self.server = server
        try:
            print "Start admin server at", cfg.ADMIN_HOST, cfg.ADMIN_PORT
            self.admin_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.admin_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)        
            self.admin_socket.bind((cfg.ADMIN_HOST, cfg.ADMIN_PORT))
            self.admin_socket.listen(cfg.ADMIN_MAX_CLIENT)
        except:
            print "Cannot create admin server socket"
            traceback.print_exc(file=sys.stdout)
            sys.exit(1)
    
    def run(self):
        while True:
           try:
               conn, addr = self.admin_socket.accept()
               # add to list client
               print("Accept admin client from ", addr)
               # create new client hander
               client = AdminClientHandler(self, conn, addr)
               client.start()
           except:
               print "CrawlerServer AdminServer exception"
               traceback.print_exc(file=sys.stdout)

class CrontabHandler(threading.Thread):
    def __init__(self, server):
        threading.Thread.__init__(self)
        self.server = server
    
    def run(self):
        while True:
            try:
                if not self.server.old_users_handler.is_running:                    
                    time.sleep(cfg.RECRAWL_TIME)
                    print "Crontab stop new thread, resume old thread"
                    self.server.new_users_handler.pause()                    
                    list_uids = self.server.db.users.find({'vn':1}).distinct('uid')
                    for u in list_uids: 
                        self.server.old_users_handler.queue.put(u)                        
                    self.server.old_users_handler.resume()
                else:
                    time.sleep(cfg.RECRAWL_TIME/2)
                    print "Crontab stop old thread, resume new thread"
                    self.server.new_users_handler.sleep_time = self.server.new_users_handler.sleep_time + 10
                    if (self.server.new_users_handler.sleep_time > 60):
                        self.server.new_users_handler.sleep_time = 60
                    self.server.new_users_handler.resume()
                    self.server.old_users_handler.pause()
                    while not self.server.old_users_handler.queue.empty():
                        self.server.old_users_handler.queue.get()
                        self.server.old_users_handler.queue.task_done()
            except:
                print "CrontabHandler exception"
                traceback.print_exc(file=sys.stdout)

class CrawlerServer(object):
    """CrawlerServer is main class run all action of server
    CrawlerServer includes:
        1 thread to accept client crawler
        2 thread to dispatch crawl request to client:
            + 1 for crawl new user. this thread was set default run when server stated
            + 1 for re crawl old user. this thread will be active after a specified time
        1 thread to accept admin client
        1 thread to pause crawl new user at specify time (4 hours) and active re crawl old user thread
    """
    
    def __init__(self, seeds):
        """ Init function
        seeds: type Array (list)
        """
        self.db = model.Database() 
        # all userid in DB
        self.list_user = {} 
        users = self.db.users.find({'vn':1}).distinct('uid')
        for u in users:
            self.list_user[u] = 1
            seeds.append(u)
                    
        print "Num of vn user", len(seeds)
        # listen server to handler request from client
        self.server = RequestHandler(self) 
        # thread to handler 
        self.new_users_handler = CrawlDispatcher(self, seeds, 0)
        self.old_users_handler = CrawlDispatcher(self, [], 0)
        # admin server
        self.admin_server = AdminServer(self)
        # recrawler thread
        self.crontab = CrontabHandler(self)
                
    def add_user_to_queue(self, uid):
        """Add new uid to crawl
        NOTE that, we need to check whether uid was crawled or not
        """
        if uid not in self.list_user:
            self.list_user[uid] = 1
            self.new_users_handler.queue.put(uid)
             
    def start(self):
        self.server.start()
        self.new_users_handler.start()
        self.old_users_handler.is_running = False
        self.old_users_handler.start()
        self.crontab.start()
        self.admin_server.start()
        
        
def main():
    if len(sys.argv) > 2:
        seeds = sys.argv[1:]
    else:
        #seeds = ['104560124403688998123', '111091089527727420853']
        seeds = []
    server = CrawlerServer(seeds)
    server.start()
    
if __name__ == "__main__":
    main()
