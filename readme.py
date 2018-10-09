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
from xml.dom.minidom import parse
import xml.dom.minidom
import yaml

# 时区定义
tz = pytz.timezone('Asia/Shanghai')

# URL定义
master_url = 'https://blog.yuanpei.me'
salver_url=  'http://qinyuanpei.github.io'

# 文档实体结构定义
class Post:

    def __init__(self,date,link,title,prefix):
        self.date  = date
        self.link  = link
        self.title = title
        self.prefix = prefix

    def getTitle(self):
        return self.title

    def getLink(self):
        return self.prefix + self.link

    def getDate(self):
        d = re.findall(r'\d{4}-\d{1,2}-\d{1,2}',self.date)[0]
        t = re.findall(r'\d{2}:\d{2}:\d{2}',self.date)[0]
        dt = '%s %s' % (d,t)
        return datetime.datetime.strptime(dt,'%Y-%m-%d %H:%M:%S')

# 从JSON中加载文档数据
def loadData(prefix):
    json_file = open('./public/content.json',mode='rt',encoding='utf-8')
    json_data = json.load(json_file)
    for item in json_data:
        yield Post(item['date'],item['path'],item['title'],prefix)

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
    with open('_config.yml', 'rt', encoding='utf-8') as f:
        conf = yaml.load(f)
        if(conf['image_version'] !="master"):
            DOMTree = xml.dom.minidom.parse('./public/baidusitemap.xml')
            root = DOMTree.documentElement
            urls = root.getElementsByTagName("url")
            for url in urls:
                loc = url.getElementsByTagName("loc")[0]
                loc.childNodes[0].data = loc.childNodes[0].data.replace(salver_url,master_url)
            with open('.public/baidusitemap.xml', 'wt',encoding='utf-8') as fi:
                fi.write(DOMTree.toprettyxml())


if(__name__ == "__main__"):
    items = sorted(loadData(sys.argv[1]),key=lambda x:x.getDate(),reverse=True)
    mkMarkdown(items)
    baiduSitemap()