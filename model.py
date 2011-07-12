from pymongo import Connection
from datetime import datetime

class Database(object):
    """Database was utility class to help interact with database
    """
    
    def __init__(self):
        connection = Connection('localhost', 27017)
        self.db = connection.gstats
        self.users = self.db.user2
        
    def insert_user_info(self, arr):
        """Insert user information to dabase
        arr: type Array(list)
            arr[1]: user id
            arr[2]: user name
            arr[3]: number of user's friends
            arr[4]: number of user's followers
            arr[5]: picture url of user
            arr[6]: sex of user (Male or Female or Other)
            arr[7]: check is vietnamese or not, 1 is VNese, 0 is not
        """
        if arr[3].isdigit() and arr[4].isdigit():
            user = {'uid':arr[1], 
                    'name':arr[2], 
                    'friends':int(arr[3]), 
                    'followers':int(arr[4]),                 
                    'pic':arr[5], 
                    'sex':arr[6], 
                    'vn' :int(arr[7]),
                    'created_on':datetime.now()}
            self.users.insert(user)
            
    def get_list_user(self):
        """Return list distinct user in database
        """
        return self.users.distinct('uid')
    
    
    
    
