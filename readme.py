#! python3
# -*- coding: utf-8 -*-
import os
import re
import sys
import json
import pytz
import datetime
from PIL import Image
from lxml import etree
from itertools import groupby
from html.parser import HTMLParser

# 时区定义
tz = pytz.timezone('Asia/Shanghai')

# URL定义
GH_URL = 'http://qinyuanpei.github.io'
CO_URL = 'http://qinyuanpei.coding.me'

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
    mdfile.write('本文档由脚本自动生成，最后更新时间：{0}\n\n'.format(
        datetime.datetime.strftime(datetime.datetime.now(tz),'%Y-%m-%d %H:%M:%S')
    ))
    mdfile.write('Hi, Payne. 从{0}至今，你撰写博客共计{1}篇，请继续努力！\n\n'.format(
        datetime.datetime.strftime(items[-1].getDate(),'%Y-%m-%d'),
        len(list(items))
    ))

    groups = groupby(items,key=lambda x:x.getDate().year)
    for key,group in groups:
        items = list(group)
        mdfile.write('# {0}(共{1}篇)\n'.format(key,len(items)))
        for item in items:
            mdfile.write(itemTpl.format(
                datetime.datetime.strftime(item.getDate(),'%Y-%m-%d'),
                item.getTitle(),
                item.getLink()
            ))

# 更新百度站点地图
def baiduSitemap():
    doc = etree.parse('./public/baidusitemap.xml')
    root = doc.getroot()
    for item in root:
        item[0].text = item[0].text.replace(GH_URL,CO_URL)
        if(len(item[2][0])<6):
            continue
        else:
            breadCrumb = item[2][0][5].attrib
            if(not breadCrumb.has_key('url')):
                continue
            else:
                breadCrumb['url'] = breadCrumb['url'].replace(GH_URL,CO_URL)

    with open('./public/baidusitemap.xml', 'wt',encoding='utf-8') as fi:
        html_parser = HTMLParser()
        xmlText = etree.tostring(root).decode('utf-8')
        xmlText = html_parser.unescape(xmlText)
        fi.write(xmlText)


if(__name__ == "__main__"):
    items = sorted(loadData(),key=lambda x:x.getDate(),reverse=True)
    mkMarkdown(items)
    baiduSitemap()