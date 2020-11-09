import os
import sys
import re
import json
import requests

url = 'https://leetcode-cn.com/u/qinyuanpei/'

# 抓取做题分析
def analyseProblems():
    resp = requests.get(url);
    print(resp.content);


analyseProblems();
# posts = listPosts('.\source\_posts')
# languages = analyseLanguages(posts)
# with open('languages.json','wt',encoding='utf-8') as f:
    #f.write(json.dumps(languages))