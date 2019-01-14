#! python3
# -*- coding: utf-8 -*-
import os
import re
import sys
import time
import json
import requests

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
    print("同步七牛图片{0}完成".format(fileKey))
    pid = upload(outfile)
    if(pid != None):
        print('同步后的图片链接为:' + upload(outfile))
        return pid

# 从CSDN下载指定图片
def sync_csdn(link):
    link = link.replace('http://img.blog.csdn.net','https://img-blog.csdn.net/')
    response = requests.get(link)
    if(response.status_code == 200):
        fileKey = link.split('/')[-1]
        outfile = root + "\\download\\blogspace\\" + fileKey  + ".jpg"
        outfile = outfile.replace('\\','/')
        if(os.path.exists(outfile)):
            os.remove(outfile)
        with open(outfile, 'wb') as fp:
            fp.write(response.content)
        print('同步CSDN图片{0}完成'.format(fileKey))
        pid = upload(outfile)
        if(pid != None):
            print('同步后的图片链接为:' + upload(outfile))
            return pid

# 下载博客中所有来自CSDN的图片
def sync(root,ak,sk,account,bucket):
    files = []
    children = os.listdir(root)
    for child in children:
        path = os.path.join(root,child)
        if os.path.isfile(path):
            files.append(path)
    for file in files:
        links = []
        newContent = ''
        with open(file,'rt',encoding='utf-8') as fp:
            content = fp.read()
            matches = re.compile('!\\[.*?\\]\\((.*?)\\)').findall(content) 
            if(len(matches)>0):
                links.extend(matches)
            for link in links:
                fileKey = link.split('/')[-1]
                if('http://img.blog.csdn.net' in link):
                    newLink = sync_csdn(link)
                    newContent = content.replace(link,newLink)
                elif('clouddn.com' in link):
                    newLink = sync_qiniu(ak,sk,account,bucket,fileKey)
                    newContent = content.replace(link,newLink)
        if(newContent!='' and len(links)>0):
            with open(file,'wt',encoding='utf-8') as fp:
                fp.write(newContent)
            print('已自动完成对{0}中图片链接的自动更新'.format(file))

# 上传图片至新浪图床
def upload(src_file):
    url = "http://picupload.service.weibo.com/interface/pic_upload.php"
    fileExt = src_file.split('.')[-1]
    if(fileExt == 'png'):
        fileExt = 'jpg'
    timestamp = str(int(time.time()))
    mimes = {"gif":'image%2Fgif','jpg':'image%2Fjpeg','jpeg':'image%2Fjpeg'}
    querystring = {"mime":mimes[fileExt],"data":"base64","url":"0","markpos":"1","logo":"","nick":"0","marks":"1","app":"miniblog","cb":"http://weibo.com/aj/static/upimgback.html?_wv=5","callback":"STK_ijax_" + timestamp}
    headers = {
        'Cookie': "SINAGLOBAL=3235885370648.688.1545903019873; UOR=www.baidu.com,open.weibo.com,login.sina.com.cn; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WF3kQ_AqPEbbcvPj8FQZhJ35JpX5KMhUgL.Fo2ES0nceh.Ee022dJLoI7yBqPLV9H8Ddntt; Ugrow-G0=8751d9166f7676afdce9885c6d31cd61; ALF=1578993480; SSOLoginState=1547457458; SCF=AvJtbZ0c6MGjVObXjJuM6TQkpI7QK5YTlzD1BQOMXHOya1sAanOyxsJV4sFQZyibn970KRwIGIo2j-ouZev94lw.; SUB=_2A25xOCPiDeRhGedM7FoX8CfOyD2IHXVSTBIqrDV8PUNbmtBeLRPGkW9NWD4ssSbmqEfywYH-f_yZTYwFHn9y4f9_; SUHB=0OMlaCp-SFOhez; wvr=6; YF-V5-G0=694581d81c495bd4b6d62b3ba4f9f1c8; _s_tentry=login.sina.com.cn; Apache=4638805556221.485.1547457462542; YF-Page-G0=86b4280420ced6d22f1c1e4dc25fe846; ULV=1547457462708:3:2:1:4638805556221.485.1547457462542:1546821645903; wb_view_log_1278609231=1920*10801",
    }
    files = {'pic1':open(src_file,'rb').read()}
    response = requests.request("POST", url, headers=headers, params=querystring,files=files)
    if(response.status_code == 200):
        result = re.sub(r"<meta.*</script>", "", response.text, flags=re.S)
        image_result = json.loads(result)
        image_id = image_result.get('data').get('pics').get('pic_1').get('pid')
        return 'https://ws1.sinaimg.cn/large/{0}.{1}'.format(image_id,fileExt)



if __name__ == "__main__":
    path = root + "\\source\\_posts"
    ak = 'n_Xh-4hMbR-kc2ad424fN0v3YCsqoD_zApWpg4Bo'
    sk = 'GZqa-JzynnnbCe_-q-AIDir1c8d_Jrk1lbVOKEU2'
    account = 'qinyuanpei@163.com'
    bucket = 'blogspace'
    sync(path,ak,sk,account,bucket)
    #sync(root,sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4])


     