#! python3
# -*- coding: utf-8 -*-
import os
import re
import sys
import time
import json
import yaml
import requests
import leancloud

# 当前根目录
root = os.path.dirname(os.path.realpath(__file__)) 

leancloud.init("JbHqRp2eMrTgIwYpfERH0g79-gzGzoHsz", "VsiKvLuiBGvJL1XrAfv7siY2")

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
    outfile = root + "\\images\\blogspace\\" + fileKey
    outfile = outfile.replace('\\','/')
    if(not os.path.exists(outfile)):
        os.system('qshell get {0} {1} -o {2}'.format(bucket,fileKey,outfile))
    print("同步七牛图片{0}完成".format(fileKey))
    pid = upload(fileKey,outfile)
    if(pid != None):
        print('同步后的图片链接为:' + pid)
        return pid
    else:
        print('同步图片失败')

# 从CSDN下载指定图片
def sync_csdn(link):
    link = link.replace('http://img.blog.csdn.net','https://img-blog.csdn.net/')
    response = requests.get(link)
    if(response.status_code == 200):
        fileKey = link.split('/')[-1]
        outfile = root + "\\images\\blogspace\\" + fileKey  + ".jpg"
        if(not os.path.exists(outfile)):
            with open(outfile, 'wb') as fp:
                fp.write(response.content)
            print('同步CSDN图片{0}完成'.format(fileKey))
        pid = upload(fileKey,outfile)
        if(pid != None):
            print('同步后的图片链接为:' + pid)
            return pid
        else:
            print('同步图片失败')

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
                    if(newLink!=None):
                        recordMigrate(fileKey,newLink)
                        newContent = content.replace(link,newLink)
                elif('clouddn.com' in link):
                    newLink = sync_qiniu(ak,sk,account,bucket,fileKey)
                    if(newLink!=None):
                        recordMigrate(fileKey,newLink)
                        newContent = content.replace(link,newLink)
                elif(os.path.exists(link)):
                    newLink = upload(link)
                    if(newLink!=None):
                        recordMigrate(fileKey,newLink)
                        newContent = content.replace(link,newLink)
        if(newContent!='' and len(links)>0):
            with open(file,'wt',encoding='utf-8') as fp:
                fp.write(newContent)
            print('已自动完成对{0}中图片链接的自动更新'.format(file))

# 上传图片至新浪图床
def upload(fileKey, src_file):
    if(not os.path.exists(src_file)):
        return None

    Record = leancloud.Object.extend('MigrateRecord')
    query = Record .query
    query.equal_to('fileKey', fileKey) 
    query_list = query.find()
    if(len(query_list)>0):
        return query_list[0].get('fileUrl')

    url = "http://picupload.service.weibo.com/interface/pic_upload.php"
    fileExt = src_file.split('.')[-1]
    if(fileExt == 'png'):
        fileExt = 'jpg'
    timestamp = str(int(time.time()))
    mimes = {"gif":'image%2Fgif','jpg':'image%2Fjpeg','jpeg':'image%2Fjpeg'}
    querystring = {"mime":mimes[fileExt],"data":"base64","url":"0","markpos":"1","logo":"","nick":"0","marks":"1","app":"miniblog","cb":"http://weibo.com/aj/static/upimgback.html?_wv=5","callback":"STK_ijax_" + timestamp}
    headers = {
        'Cookie': "UOR=caibaojian.com,widget.weibo.com,caibaojian.com; _s_tentry=-; Apache=6274615450455.858.1548402217686; SINAGLOBAL=6274615450455.858.1548402217686; ULV=1548402217693:1:1:1:6274615450455.858.1548402217686:; Ugrow-G0=56862bac2f6bf97368b95873bc687eef; login_sid_t=75730530def94dc01820a4d18813433b; cross_origin_proto=SSL; YF-V5-G0=b59b0905807453afddda0b34765f9151; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WF3kQ_AqPEbbcvPj8FQZhJ35JpX5K2hUgL.Fo2ES0nceh.Ee022dJLoI7yBqPLV9H8Ddntt; ALF=1579940557; SSOLoginState=1548404557; SCF=Aufk6qaFoXzTDSSsv0RnBDk0gdwkcbV6idQcE5TslwevDgGcc2pVALkxHgf-oufIxURNpe-f8Pa_gFK5Quzk3cs.; SUB=_2A25xTrceDeRhGedM7FoX8CfOyD2IHXVSPa_WrDV8PUNbmtBeLRaskW9NWD4ssQkRGWHEiliD3L74aCTlqPI8bIU_; SUHB=0rr69ErrdfloKc; un=qinyuanpei@sina.com; wvr=6; YF-Page-G0=19f6802eb103b391998cb31325aed3bc; wb_view_log_1278609231=1920*10801",
    }
    files = {'pic1':open(src_file,'rb').read()}
    response = requests.request("POST", url, headers=headers, params=querystring,files=files)
    if(response.status_code == 200):
        result = re.sub(r"<meta.*</script>", "", response.text, flags=re.S)
        image_result = json.loads(result)
        image_id = image_result.get('data').get('pics').get('pic_1').get('pid')
        return 'https://ws1.sinaimg.cn/large/{0}.{1}'.format(image_id,fileExt)

# 本队图片与远程图片关系维护
def recordMigrate(fileKey,fileUrl):
    Record = leancloud.Object.extend('MigrateRecord')
    record = Record()
    record.set('fileKey', fileKey)
    record.set('fileUrl', fileUrl)
    now = time.localtime(time.time())
    record.set('migrateDate', time.strftime("%Y-%m-%d %H:%M:%S", now))
    record.set('migrateBy', 'qinyuanpei@163.com')
    record.save()


if __name__ == "__main__":
    path = root + "\\source\\_posts"
    ak = 'n_Xh-4hMbR-kc2ad424fN0v3YCsqoD_zApWpg4Bo'
    sk = 'GZqa-JzynnnbCe_-q-AIDir1c8d_Jrk1lbVOKEU2'
    account = 'qinyuanpei@163.com'
    bucket = 'blogspace'
    sync(path,ak,sk,account,bucket)
    #sync(root,sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4])
