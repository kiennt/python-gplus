# -*- coding: utf8 -*-
import sys
from pymongo import Connection

SIGN_CHARS = ['a', 'á', 'à', 'ả', 'ã', 'ạ', 
             'â', 'ấ', 'ầ', 'ẩ', 'ẫ', 'ậ', 
             'ă', 'ắ', 'ằ', 'ẳ', 'ẵ', 'ặ', 
             'e', 'é', 'è', 'ẻ', 'ẽ', 'ẹ', 
             'ê', 'ế', 'ề', 'ể', 'ễ', 'ệ',
             'i', 'í', 'ì', 'ỉ', 'ĩ', 'ị',
             'o', 'ó', 'ò', 'ỏ', 'õ', 'ọ',
             'ô', 'ố', 'ồ', 'ổ', 'ỗ', 'ộ',
             'ơ', 'ớ', 'ờ', 'ở', 'ỡ', 'ợ',
             'ư', 'ứ', 'ừ', 'ử', 'ữ', 'ự',
             'u', 'ú', 'ù', 'ủ', 'ũ', 'ụ',
             'đ']
NORM_CHARS = ['a', 'a', 'a', 'a', 'a', 'a', 
              'a', 'a', 'a', 'a', 'a', 'a', 
              'a', 'a', 'a', 'a', 'a', 'a', 
              'e', 'e', 'e', 'e', 'e', 'e', 
              'e', 'e', 'e', 'e', 'e', 'e',
              'i', 'i', 'i', 'i', 'i', 'i',
              'o', 'o', 'o', 'o', 'o', 'o',
              'o', 'o', 'o', 'o', 'o', 'o',
              'o', 'o', 'o', 'o', 'o', 'o',
              'u', 'u', 'u', 'u', 'u', 'u',
              'u', 'u', 'u', 'u', 'u', 'u',
              'd']

class VietnameseDetect(object):
    def __init__(self):
        f = open("/home/gstats/syllable.vn")
        words = f.readlines()
        self.words = {}
        for word in words:
            word = word[:-1]
            self.words[word] = 1
            norm_word = self.remove_sign(word)
            self.words[norm_word] = 1
        
    
    def remove_sign(self, word):
        for i in range(len(SIGN_CHARS)):
            word = word.replace(SIGN_CHARS[i], NORM_CHARS[i])
        return word
        
    def check_name(self, name):
        if name is None: 
            return False
        tokens = name.split()
        score = 0
        total_len = 0
        for token in tokens:
            token = token.lower()
            token_len = len(token)
            if token_len > 2:
                total_len = total_len + token_len
                if token in self.words:
                    score = score + token_len
                else:
                    score = score - len(token)
        if total_len > 0:
            score = score * 1.0/total_len
            if score > 0.1:
                return True
        return False     
            

def main():
    detector = VietnameseDetect()
    if len(sys.argv) > 1:
        for name in sys.argv[1:]:
            is_vn = detector.check_name(name)
            if is_vn: 
                print name, ': la ten tieng viet'
            else:
                print name, ': khong phai'
    else:
        c = Connection("localhost", 27017)
        users = c.gstats.user2
        count = 0
        for u in users.find({}):
            is_vn = detector.check_name(u['name'])
            if is_vn:
                u['vn'] = 1
                print u['uid'], u['name'], u['friends'], u['followers']                 
                count = count + 1
            else:
                u['vn'] = 0
            users.save(u)
        print "Tong so ten TV:", count
    

if __name__ == "__main__":
    main()
        
