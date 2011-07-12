import subprocess
import time
import threading

class ServerThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        subprocess.call(['python', '/home/gstats/crawler_server.py'])

class ClientThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        subprocess.call(['python', '/home/gstats/crawler_client.py'])

def main():
    server = ServerThread()
    server.start()
    time.sleep(2)

    for i in range(10):
        client = ClientThread()
        client.start()


if __name__ == "__main__":
    main()
