#! python3
# -*- coding: utf-8 -*-
import os
import re
import sys
import time
import json
import requests
import weibo

# 当前根目录
root = os.path.dirname(os.path.realpath(__file__)) 

# 从七牛下载指定仓库内全部图片 
def sync_quniu_all(ak,sk,account,bucket):
    os.system('qshell account {0} {1} {2} -w'.format(ak,sk,account))
    print('开始从仓库{0}中下载图片'.format(bucket))
    os.system('qshell listbucket {0} -o list.txt'.format(bucket))
    with open('./list.txt','rt',encoding='utf-8') as fp:
        for line in fp:
            fileKey = line.split('\t')[0]
            os.system('qshell get {0} {1} -o {2}'.format(bucket,fileKey))
            print("下载图片{0}完成".format(fileKey))

# 从七牛下载指定仓库内指定图片
def sync_qiniu(ak,sk,account,bucket,fileKey):
    os.system('qshell account {0} {1} {2} -w'.format(ak,sk,account))
    outfile = root + "\\download\\blogspace\\" + fileKey
    outfile = outfile.replace('\\','/')
    if(os.path.exists(outfile)):
        os.remove(outfile)
    os.system('qshell get {0} {1} -o {2}'.format(bucket,fileKey,outfile))
    print("下载图片{0}完成".format(fileKey))
    print(upload(outfile))

# 从CSDN下载指定图片
def sync_csdn(link):
    response = requests.get(link)
    if(response.status_code == 200):
        fileKey = link.split('/')[:-1]
        outfile = root + "\\download\\blogspace\\" + fileKey  + ".jpg"
        outfile = outfile.replace('\\','/')
        if(os.path.exists(outfile)):
            os.remove(outfile)
        with open(outfile, 'wb') as fp:
            f.write(response.content)
        print('下载图片{0}完成'.format(fileKey))
        print(upload(outfile))

# 下载博客中所有来自CSDN的图片
def sync(root,ak,sk,account,bucket):
    files = []
    children = os.listdir(root)
    for child in children:
        path = os.path.join(root,child)
        if os.path.isfile(path):
            files.append(path)
    links = []
    for file in files:
        with open(file,'rt',encoding='utf-8') as fp:
            content = fp.read()
            matches = re.compile('!\\[.*?\\]\\((.*?)\\)').findall(content) 
            if(len(matches)>0):
                links.extend(matches)
    for link in links:
        fileKey = link.split('/')[-1]
        if('http://img.blog.csdn.net' in link):
            sync_csdn(link)
        elif('http://7wy477.com1.z0.glb.clouddn.com' in link):
            sync_qiniu(ak,sk,account,bucket,fileKey)

# 上传图片至新浪图床
def upload(src_file):
    return weibo.get_image(src_file,'1546821636','WEIBO85374216')


if __name__ == "__main__":
    path = root + "\\source\\_posts"
    ak = 'n_Xh-4hMbR-kc2ad424fN0v3YCsqoD_zApWpg4Bo'
    sk = 'GZqa-JzynnnbCe_-q-AIDir1c8d_Jrk1lbVOKEU2'
    account = 'qinyuanpei@163.com'
    bucket = 'blogspace'
    sync(path,ak,sk,account,bucket)
    #sync(root,sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4])


     