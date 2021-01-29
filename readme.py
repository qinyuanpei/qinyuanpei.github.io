#! python3
# -*- coding: utf-8 -*-
import os
import re
import sys
import time
import json
import pytz
import datetime
import requests
from PIL import Image
from lxml import etree
from itertools import groupby
from html.parser import HTMLParser
from xml.dom.minidom import parse
import xml.dom.minidom
import yaml
# import leancloud

# 时区定义
tz = pytz.timezone('Asia/Shanghai')

# URL定义
master_url = 'https://blog.yuanpei.me/'
salver_url=  'http://qinyuanpei.github.io/'

# 百度地址提交定义
baseUrl = "http://data.zz.baidu.com/urls?site=https://blog.yuanpei.me&token=RDl7DmfXeoWMVvWP"
querystring = {"site":"","token":"RDl7DmfXeoWMVvWP"}
headers = {
    'User-Agent': "curl/7.12.1",
    'Content-Type': "text/plain",
}

# leancloud.init("JbHqRp2eMrTgIwYpfERH0g79-gzGzoHsz", "VsiKvLuiBGvJL1XrAfv7siY2")
# UrlSubmit = leancloud.Object.extend('UrlSubmit')

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
        return self.prefix + '/' + self.link

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
    commitHash = open('VERSION.txt', 'r', encoding='utf-8').readlines()[0]
    mdfile.write("[![Build Status](https://www.travis-ci.org/qinyuanpei/qinyuanpei.github.io.svg?branch=blog)](https://www.travis-ci.org/qinyuanpei/qinyuanpei.github.io)\n")
    mdfile.write("[![jsDelivr](https://data.jsdelivr.com/v1/package/gh/qinyuanpei/qinyuanpei.github.io/badge)](https://www.jsdelivr.com/package/gh/qinyuanpei/qinyuanpei.github.io)\n\n")
    mdfile.write('本文档由脚本自动生成，最后更新时间：{0}，最后部署版本：[{1}]({2})\n\n'.format(
        datetime.datetime.strftime(datetime.datetime.now(tz),'%Y-%m-%d %H:%M:%S'),
        commitHash[0:7],
        'https://github.com/qinyuanpei/qinyuanpei.github.io/commit/' + commitHash
    ))
    mdfile.write('如果想订阅我的博客，请使用Github的Watch功能，**请不要fork此项目**\n\n')
    mdfile.write('Hi, Payne. 从{0}至今，你撰写博客共计{1}篇，请继续努力！\n\n'.format(
        datetime.datetime.strftime(items[-1].getDate(),'%Y-%m-%d'),
        len(list(items))
    ))
    mdfile.write("Coding Pages版本：[https://blog.yuanpei.me](https://blog.yuanpei.me)\n\n")
    mdfile.write("Github Pages版本：[https://qinyuanpei.github.io](https://qinyuanpei.github.io)\n\n")

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

# 提交地址
def submitSitemap():
    with open('_config.yml', 'rt', encoding='utf-8') as f:
        conf = yaml.load(f)
        session = requests.session()
        if(conf['image_version'] == "master"):

            DOMTree = xml.dom.minidom.parse('./public/baidusitemap.xml')
            root = DOMTree.documentElement
            urls = root.getElementsByTagName("url")
            for url in urls:
                loc = url.getElementsByTagName("loc")[0]
                payload = loc.childNodes[0].data
                print(payload)
                if not querySubmitHistory(url) == 0:
                    response = session.request("POST", baseUrl, data=payload, headers=headers,)
                    print(response.text)
                    data = json.loads(response.text)
                    if(data['success'] == 1):
                        print('提交地址:{payload},至百度成功'.format(payload=payload))
                        createSubmitHistory(url)
                    time.sleep(5)

# 查询提交记录
def querySubmitHistory(url):
    if not os.path.exists('urlSubmit.json'):
        return False
    else:
        with open('urlSubmit.json', 'rt', encoding='utf-8') as fp:
            histories = json.load(fp)
            if url in histories:
                return True
            else:
                return False

# 创建提交记录
def createSubmitHistory(url):
    histories = []
    if os.path.exists('urlSubmit.json'):
        with open('urlSubmit.json', 'rt', encoding='utf-8') as fp:
            histories = json.load(fp)
    histories.append(url)
    with open('urlSubmit.json', 'wt', encoding='utf-8') as fp:
        json.dump(histories, fp)

if(__name__ == "__main__"):
    items = sorted(loadData(sys.argv[1]),key=lambda x:x.getDate(),reverse=True)
    mkMarkdown(items)
    baiduSitemap()
    submitSitemap()