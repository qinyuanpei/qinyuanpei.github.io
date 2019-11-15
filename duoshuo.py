#! python3
# -*- coding: utf-8 -*-
import os
import re
import sys
import time
import json
from datetime import datetime
import leancloud

# 当前根目录
root = os.path.dirname(os.path.realpath(__file__))

leancloud.init("JbHqRp2eMrTgIwYpfERH0g79-gzGzoHsz", "VsiKvLuiBGvJL1XrAfv7siY2")
Comment = leancloud.Object.extend('Comment')

def convert(): 
    output = []
    with open(os.path.join(root,'export.json')) as f:
        data = json.load(f)
        threads = data['threads']
        posts = data['posts']
        for post in list(filter(lambda p:not p['message']=='' ,posts)):
            for thread in threads:
                if(post['thread_id'] == thread['thread_id']):
                    output.append((thread['title'],post['message'],post['author_email'],post['author_name'],post['author_url'],post['parents']))
        
    return output
        
def transfer(source):
    with open(os.path.join(root,'public/content.json'),encoding='utf-8') as f:
        data = json.load(f)
        for item in source:
            # posts = list(filter(lambda x:x['title'] == item[0], data))
            # if len(posts) > 0:
            #     item = item + ('https://blog.yuanpei.me/' + posts[0]['path'],)
            #     if(item[5] == None):
            #         comment = Comment()
            #         comment.set('nick',item[3])
            #         comment.set('mail',item[2])
            #         comment.set('link',item[4])
            #         comment.set('comment',item[1])
            #         comment.set('url', item[6])
            #         comment.set('insertedAt', datetime.now())
            #         comment.save()

            if item[0] == '关于':
                item = item + ('https://blog.yuanpei.me/about',)
                print(item)
                if(item[5] == None or len(item[5]) == 0):
                    comment = Comment()
                    comment.set('nick',item[3])
                    comment.set('mail',item[2])
                    comment.set('link',item[4])
                    comment.set('comment',item[1])
                    comment.set('url', item[6])
                    comment.set('insertedAt', datetime.now())
                    comment.save()


source = convert()
transfer(source)

