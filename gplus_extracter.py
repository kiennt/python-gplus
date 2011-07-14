import urllib2
import sys
import traceback
from sets import Set

import cfg

class GplusExtracter(object):
    """Extract information from G+ with specific user id
    """
    def __init__(self, main, id, proxy):
        self.main = main
        self.uid = id
        self.friends = 0
        self.followers = 0
        self.proxy = proxy
        proxy_handler = urllib2.ProxyHandler({'https':proxy})
        self.opener = urllib2.build_opener(proxy_handler)
                          
    def get_name_of_user(self, content):
        try:
            idx1 = content.find('<span class="fn">')
            content = content[idx1 + 17:]
            idx2 = content.find('<')
            name = content[:idx2]
            return name
        except:
            print "Exception when get name of user:"
            #traceback.print_exc(file=sys.stdout)
            raise

    def get_number_of_friends(self, content):
        try:
            idx1 = content.find('<h4 class="a-c-ka-Sf d-s-r">')
            if idx1 > -1:
                content = content[idx1 + 28:]
                idx2 = content.find('(')
                idx3 = content.find(')')
                num_of_friends = content[idx2 + 1:idx3]
                if num_of_friends.isdigit():
                    return num_of_friends
            return str(self.friends)
        except:
            print "Exception when get number of user"
            traceback.print_exc(file=sys.stdout)
            raise

    def get_number_of_follows(self, content):
        try:
            idx1 = content.find('<h4 class="a-c-ka-Sf">')
            if idx1 > -1:
                content = content[idx1 + 23:]
                idx2 = content.find('(')
                idx3 = content.find(')')
                num_of_follows = content[idx2 + 1:idx3]
                if num_of_follows.isdigit():
                    return num_of_follows
            return str(self.followers)
        except:
            print "Exception when get number of followers:"
            #traceback.print_exc(file=sys.stdout)
            raise

    def get_sex_of_user(self, content):
        try:
            idx1 = content.find('Gender</h2><div class="a-c-B-F-Oa d-s-r">')
            if idx1 > -1:
                content = content[idx1 + 41:]
                idx2 = content.find('<')
                sex = content[:idx2]
                if sex == 'Male' or sex == 'Female':
                   return sex
            return "Other"    
        except:
            print "Exception when get sex of user:"
            #traceback.print_exc(file=sys.stdout)
            raise


    def get_user_picture(self, content):
        try:
            idx1 = content.find('img alt="" class="a-b-c-z-pa photo" width="200" height="200" src="')
            if idx1 > -1:
                content = content[idx1 + 66:]
                idx2 = content.find('"')
                pic = content[:idx2]
                return 'http:' + pic[:-7]
            return ""
        except:
            print "Exception when get pic of user:"
            traceback.print_exc(file=sys.stdout)
            raise

    def get_user_info(self): 
        try:     
            print "---------------------------------------------"
            # if we want to process by english, we should use another link
            #url = "https://plus.google.com/" + self.uid + "/about?hl=en"
            url = "https://plus.google.com/" + self.uid + "/about?hl=en" 
            print "Connecting to url", url
            f = self.opener.open(url)
            content = f.read()
            #print "Process content"
            name = self.get_name_of_user(content)
            #print "Name:", name
            sex = self.get_sex_of_user(content)
            #print "Sex:", sex
            num_of_friends = self.get_number_of_friends(content)
            #print "Friends:", num_of_friends
            num_of_follows = self.get_number_of_follows(content)
            #print "Follows:", num_of_follows
            pic = self.get_user_picture(content)
            print "Pic:", pic
            msg = cfg.MSG_USER_INFO + "," + self.uid + "," + name + "," + num_of_friends + "," + num_of_follows + "," + pic + "," + sex + ",1"
            return msg
        except:
            print "Exception when get_user_info:" , self.uid, "with proxy:", self.proxy
            #traceback.print_exc(file=sys.stdout)
            raise        

    def parse(self, content):
        stack = []
        current_arr = []
        stack.append(current_arr)
        new_value = []
        wait_new_value = True
        for ch in content:
            if ch == '[':
                # add new array in stack
                new_arr = []
                current_arr.append(new_arr)
                stack.append(new_arr)
                # prepare new value
                current_arr = new_arr
                wait_new_value = True
            elif ch == ']':
                # push current value
                if wait_new_value and len(current_arr) > 0:
                    current_arr.append(None)
                wait_new_value = False
                # end of array
                stack.pop()
                current_arr = stack[-1]
            elif ch == ',':
                if wait_new_value:
                    current_arr.append(None)
                # prepare new value
                wait_new_value = True
            elif ch == '\"':
                # begin new value
                if wait_new_value: 
                    wait_new_value = False
                    new_value = []
                else:
                    value = ''.join(new_value)
                    current_arr.append(value)
            else:
                new_value.append(ch)
        return current_arr[0]

    def get_list_user(self, url):
        try:
            f = self.opener.open(url)
            content = ''
            for line in f.readlines()[1:]: 
                content = content + line[:-1]
            #print content
            arr = self.parse(content)
            arr = arr[2]
            return arr
        except:
            print "Exception when get_list_user with proxy", self.proxy
            #traceback.print_exc(file=sys.stdout)
            raise
                
    def get_user_friends(self):
        url = "https://plus.google.com/_/socialgraph/lookup/visible/?o=%5Bnull%2Cnull%2C%22" + self.uid + "%22%5D&n=1000"
        arr = self.get_list_user(url)
        if arr is not None:
            self.friends = len(arr)
        return arr
        
    
    def get_followers_user(self):
        url = "https://plus.google.com/_/socialgraph/lookup/incoming/?o=%5Bnull%2Cnull%2C%22" + self.uid + "%22%5D&n=1000"
        arr = self.get_list_user(url)
        if arr is not None:
            self.followers = len(arr)
        return arr
        
    def get_friends_info(self):
        msg = cfg.MSG_LIST_USERS
        
        friends = self.get_user_friends()        
        if friends is not None:
            vn_friends = []
            for f in friends:
                name = f[2][0]
                if self.main.vd.check_name(name):
                    vn_friends.append(f[0][2])
            if len(vn_friends) > 0:
                msg = msg + ',' +  ','.join(vn_friends)
                
        followers = self.get_followers_user()
        if followers is not None:
            vn_followers = []
            for f in followers:
                name = f[2][0]
                if self.main.vd.check_name(name):
                    vn_followers.append(f[0][2])
            if len(vn_followers) > 0:
                msg = msg + ',' + ','.join(vn_followers)
                
        return msg
        
        
def main():
    res = get_friends('111091089527727420853')
    print res
                
if __name__ == "__main__":
    main()
