import subprocess
import time
import threading

class ServerThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        cmd = "python /home/gstats/crawler_server.py >> /home/gstats/log/server"
        subprocess.Popen(cmd, shell=True)

class ClientThread(threading.Thread):
    def __init__(self, i):
        self.id = i
        threading.Thread.__init__(self)

    def run(self):
        cmd = 'python /home/gstats/crawler_client.py >> /home/gstats/log/client0' + self.id
        subprocess.Popen(cmd, shell=True)

def main():
    server = ServerThread()
    server.start()
    time.sleep(2)

    for i in range(10):
        client = ClientThread(str(i))
        client.start()


if __name__ == "__main__":
    main()
