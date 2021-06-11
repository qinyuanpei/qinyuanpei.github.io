import os
import re
import sys
import time
import json
import pytz
import datetime
import requests
from lxml import etree
from itertools import groupby
from html.parser import HTMLParser
from xml.dom.minidom import parse
import xml.dom.minidom

querystring = {"site": "blog.yuanpei.me", "token": "RDl7DmfXeoWMVvWP"}
headers = {
    'User-Agent': "curl/7.12.1",
    'Content-Type': "text/plain",
}


def submitSitemap(baseUrl):
    session = requests.session()
    response = session.get(baseUrl + '/baidusitemap.xml')
    with open('baidusitemap.xml','w',encoding='utf-8') as sitemap:
        sitemap.write(response.text);
    DOMTree = xml.dom.minidom.parse('./baidusitemap.xml')
    root = DOMTree.documentElement
    urls = root.getElementsByTagName("url")
    for url in urls:
        loc = url.getElementsByTagName("loc")[0]
        payload = loc.childNodes[0].data
        response = session.request("POST", 'http://data.zz.baidu.com/urls', data=payload, headers=headers, params=querystring)
        print(response.text)
        data = json.loads(response.text)
        if('success' in data and data['success'] == 1):
            print('提交地址:{payload},至百度成功'.format(payload=payload))
        time.sleep(5)


if(__name__ == "__main__"):
    submitSitemap(sys.argv[1])
