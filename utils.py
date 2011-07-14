from pymongo import Connection
from pymongo import ASCENDING, DESCENDING
import pymongo
import sys

class DatabaseUtils(object):
    def __init__(self):
        connection = Connection('localhost', 27017)
        self.db = connection.gstats
        self.users = self.db.user2
    
    def get_distinct_user(self):
        print "distinct user"
        print len(self.users.distinct('uid'))
        
        
    def get_info_of_user(self):
        print "distinct user"
        print len(self.users.distinct('uid'))
        print "count users", self.users.find({}).count()

        
    def clear_all_users(self):
        self.users.remove()
                
    
    def print_all_user(self):
        for u in self.users.find({}): 
            print "------------------------------"
            print u['uid'], u['name'], u['friends'], u['followers'], u['sex']
    
    def print_sex_info(self):
        count_male = self.users.find({'sex':'Male'}).count()
        count_female = self.users.find({'sex':'Female'}).count()
        count_other = self.users.find({'sex':'Other'}).count()
        total = count_male + count_female + count_other
        print '----------------------------------------------'
        print 'Total :', total
        if total > 0:
            print 'Male  :', count_male, '=', count_male * 100.0/total, '%'
            print 'Female:', count_female, '=', count_female * 100.0/total, '%'
            print 'Other :', count_other, '=', count_other * 100.0/total, '%'
    
    def date(self):
        begin = self.users.find({}).sort([('created_on',pymongo.ASCENDING)]).limit(1)[0]['created_on']
        end = self.users.find({}).sort([('created_on',pymongo.DESCENDING)]).limit(1)[0]['created_on']
        print begin
        print end
    
    def get_vn(self):
        print len(self.users.find({'vn':1}).distinct('uid'))

    def sort_friends_vn(self):
        vnusers = self.users.find({'vn':1}).sort([('friends', DESCENDING)]).limit(50)
        for u in vnusers:
            print u['uid'], u['name'], u['friends'], u['followers']
        print 'Total: ', vnusers.count()
            
    def sort_followers_vn(self):
        vnusers = self.users.find({'vn':1}).sort([('followers', DESCENDING)]).limit(50)
        for u in vnusers:
            print u['uid'], u['name'], u['friends'], u['followers']
        print 'Total: ', vnusers.count()

def main():
    db = DatabaseUtils()
    command = sys.argv[1]    
    if command == "clear":
        db.get_distinct_user()
        db.clear_all_users()   
        db.get_distinct_user()
    if command == "info":
        db.get_info_of_user()
    if command == "distinct":
        db.get_distinct_user()
    if command == "print":
        db.print_all_user()
    if command == "sex":
        db.print_sex_info()
    if command == "vn":
        db.get_vn()
    if command == "fr_vn":
        db.sort_friends_vn()
    if command == "fl_vn":
        db.sort_followers_vn()
    if command == "date":
        db.date()

if __name__ == "__main__":
    main()
