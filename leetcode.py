import os
import sys
import re
import json
import requests
import asyncio
from pyppeteer import launch

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

async def main():
    browser = await launch({
        'headless':False
    })  # 启动浏览器
 
    page = await browser.newPage()  # 打开新页面tab
    await page.goto('https://leetcode-cn.com', {
        'timeout': 1000 * 60 * 10
    })
    await page.screenshot({'path': 'baidu_screenshot.png'})  # 截图。/VSCode的当前项目目录/图片.png
 
    await browser.close()  # 关闭浏览器
 
asyncio.get_event_loop().run_until_complete(main())