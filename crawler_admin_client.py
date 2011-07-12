import socket
import threading
import sys
import traceback

import cfg

class InputHandler(threading.Thread):
    """InputHandler handler user input"""
    def __init__(self, main):
        """Init function
        main: type CrawlerAdminClient
        """
        threading.Thread.__init__(self)
        self.main = main
        
    def is_validate(self, cmd):  
        return True
        return cmd in [cfg.AdminMessage.TOTAL_UID_CLIENT_CRAWLED] or cmd in [cfg.AdminMessage.COUNT_USER]
               
    def run(self):
        while True:
            try:
                cmd = raw_input("> ")
                if self.is_validate(cmd):
                    self.main.socket.send(cmd)
                else:
                    print "Unknown command'", cmd, "'"
            except:
                print "Exception when run InputHandler "
                traceback.print_exc(file=sys.stdout)

class NetHandler(threading.Thread):
    """NetHandler handler input data from network"""
    def __init__(self, main):
        """Init function
        main: type CrawlerAdminClient
        """
        threading.Thread.__init__(self)
        self.main = main
        
    def run(self):
        while True:
            try:
                data = self.main.socket.recv(cfg.BUF_SIZE)
                print data
                sys.stdout.write("> ")
                sys.stdout.flush()
            except:
                print "Exception when run NetHandler "
                traceback.print_exc(file=sys.stdout)

class CrawlerAdminClient(threading.Thread):
    """CrawlerAdminClient is admin client to inject to crawl server
    """
    def __init__(self):
        threading.Thread.__init__(self)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.input_handler = InputHandler(self)
        self.net_handler = NetHandler(self)
    
    def run(self):
        try:
            self.socket.connect((cfg.ADMIN_HOST, cfg.ADMIN_PORT))
            print "Connect to crawler server success"
            
            self.input_handler.start()
            self.net_handler.start()
        except:
            print "Cannot connect to crawler server"
            traceback.print_exc(file=sys.stdout)
            sys.exit(1)
    
def main():
    admin_client = CrawlerAdminClient()
    admin_client.start()

if __name__ == "__main__":
    main()