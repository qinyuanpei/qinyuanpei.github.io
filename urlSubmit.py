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

baseUrl = "http://data.zz.baidu.com/urls?site=https://blog.yuanpei.me&token=RDl7DmfXeoWMVvWP"
querystring = {"site":"","token":"RDl7DmfXeoWMVvWP"}
headers = {
    'User-Agent': "curl/7.12.1",
    'Content-Type': "text/plain",
}

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
                response = session.request("POST", baseUrl, data=payload, headers=headers,)
                print(response.text)
                data = json.loads(response.text)
                if(data['success'] == 1):
                    print('提交地址:{payload},至百度成功'.format(payload=payload))
                time.sleep(5)



if(__name__ == "__main__"):
    submitSitemap()