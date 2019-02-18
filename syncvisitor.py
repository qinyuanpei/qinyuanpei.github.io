#! python3
# -*- coding: utf-8 -*-
import os
import re
import sys
import time
import json
import yaml
import requests
import leancloud

# 当前根目录
root = os.path.dirname(os.path.realpath(__file__)) 

leancloud.init("JbHqRp2eMrTgIwYpfERH0g79-gzGzoHsz", "VsiKvLuiBGvJL1XrAfv7siY2")

#获取卜蒜子访问量
def getVisitCount(post_url):
    url = "http://busuanzi.ibruce.info/busuanzi"
    querystring = {"jsonpCallback":"BusuanziCallback_1046609647591"}
    payload = ""
    headers = {
        'Referer': post_url,
    }
    response = requests.request("GET", url, data=payload, headers=headers, params=querystring)
    if(response.status_code!=200):
        return 0
    else:
        result = response.text
        result = result.replace('try{BusuanziCallback_1046609647591(','')
        result = result.replace(');}catch(e){}','')
        print('已抓取不蒜子统计:' + result)
        return json.loads(result)['page_pv']

# 同步不蒜子访问量
def syncVisitCount():
    with open('_config.yml', 'rt', encoding='utf-8') as f:
        conf = yaml.load(f)
        baseUrl = conf['url']
        json_file = open('./public/content.json',mode='rt',encoding='utf-8')
        json_data = json.load(json_file)
        for item in json_data:
            post_id = item['path'].split('/')[1]
            post_url = item['path']
            post_title = item['title']
            print('开始从不蒜子抓取文章:' + post_title + "的访问量")
            url = conf['url'] + "/"  + post_url
            Counter = leancloud.Object.extend('Counter')
            counter = None
            query = Counter.query
            query.equal_to('post_id', post_id) 
            query_list = query.find()
            if(len(query_list) > 0):
                counter = Counter.create_without_data(query_list[0].id)
                if(conf['image_version'] == 'master'):
                    master_pv = getVisitCount(url)
                    salve_pv = int(query_list[0].get('salve_pv'))
                else:
                    master_pv = query_list[0].get('master_pv')
                    salve_pv = int(getVisitCount(url))
                counter.set('master_pv',str(master_pv))
                counter.set('salve_pv',str(salve_pv))
                counter.set('total_pv',str(master_pv + salve_pv))
            else:
                counter = Counter()
                counter.set('post_id',post_id)
                counter.set('post_url',post_url)
                counter.set('post_title',post_title)
                if(conf['image_version'] == 'master'):
                    master_pv = getVisitCount(url)
                    salve_pv = 0
                else:
                    master_pv = 0
                    salve_pv = getVisitCount(url)
                counter.set('master_pv',str(master_pv))
                counter.set('salve_pv',str(salve_pv))
                counter.set('total_pv',str(master_pv + salve_pv))
            counter.save()
            print('已完成不蒜子访问量的同步')

if __name__ == "__main__":
    syncVisitCount()
