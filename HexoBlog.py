# -*- coding: utf-8 -*-

import os
import re
import sys
import json
import datetime
from itertools import groupby

# 文档实体结构定义
class Post:

    def __init__(self,date,link,title):
        self.date  = date
        self.link  = link
        self.title = title

    def getTitle(self):
        return self.title

    def getLink(self):
        return 'https://qinyuanpei.github.io/' + self.link

    def getDate(self):
        d = re.findall(r'\d{4}-\d{1,2}-\d{1,2}',self.date)[0]
        t = re.findall(r'\d{2}:\d{2}:\d{2}',self.date)[0]
        dt = '%s %s' % (d,t)
        return datetime.datetime.strptime(dt,'%Y-%m-%d %H:%M:%S')

# 从JSON中加载文档数据
def loadData():
    json_file = open('./public/content.json',mode='rt',encoding='utf-8')
    json_data = json.load(json_file)
    for item in json_data:
        yield Post(item['date'],item['path'],item['title'])

# 从列表生成Markdown文件
def mkMarkdown(items):
    mdfile = open('README.md',mode='wt',encoding='utf-8')
    itemTpl = '* {0} - [{1}]({2})\n'
    mdfile.write('本文档由脚本自动生成，最后更新时间：{0}\n'.format(
        datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d %H:%M:%S')
    ))

    groups = groupby(items,key=lambda x:x.getDate().year)
    for key,group in groups:
        items = list(group)
        mdfile.write('# {0}({1})\n'.format(key,len(items)))
        for item in items:
            mdfile.write(itemTpl.format(
                datetime.datetime.strftime(item.getDate(),'%Y-%m-%d'),
                item.getTitle(),
                item.getLink()
            ))
    



if(__name__ == "__main__"):
    items = sorted(loadData(),key=lambda x:x.getDate(),reverse=True)
    mkMarkdown(items)
