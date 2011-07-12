# server configuration
HOST = 'localhost'
PORT = 17788
MAX_CLIENT = 10

# admin configuration
ADMIN_HOST = 'localhost'
ADMIN_PORT = 22880
ADMIN_MAX_CLIENT = 1

# max buffer size
BUF_SIZE = 1000

# message configuration
MSG_USER_INFO = '1'
MSG_LIST_USERS = '2'

# client configuration
MAX_THREAD_PER_CLIENT = 10

# recrawl time
RECRAWL_TIME = 7200

class AdminMessage(object): 
    COUNT_USER = ["count_user", "cu"]
    COUNT_CLIENT = ["count_client", "cl"]
    PAUSE_CRAWL_NEW = ["pause_crawl_new", "pn"]
    RESUME_CRAWL_NEW = ["resume_crawl_new", "rn"]
    QUEUE_NEW = ["queue_new", "qn"]
    
    PAUSE_CRAWL_OLD = ["pause_crawl_old", "po"]    
    RESUME_CRAWL_OLD = ["resume_crawl_new", "ro"]
    QUEUE_OLD = ["queue_old", "qo"]
    
    STATUS = ["status", "stt"]
    TOTAL_UID_CLIENT_CRAWLED = ["total_uid_client_crawled", "tu"]
    CACHE_MISS_RATED = ["cache_miss","cm"]