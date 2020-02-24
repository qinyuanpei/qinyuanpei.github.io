import os
import sys
import re
import json

# 列举所有博客
def listPosts(rootPath):
    posts = []
    children = os.listdir(rootPath)
    for child in children:
        filePath = os.path.join(rootPath,child)
        if os.path.isfile(filePath):
            posts.append(filePath)
        else:
            posts.extend(listPosts(filePath))
    return posts

# 分析语言使用情况
def analyseLanguages(posts):
    languages = {}
    for post in posts:
        fi = open(post,'rt',encoding='utf-8')
        text = list(map(lambda x:x.strip().replace('\n','').replace('\t',''), fi.readlines()))
        matches = list(filter(lambda x:x.startswith('```') and len(x) > 3, text))
        if len(matches) > 0:
            for match in matches:
                language = match[3:]
                if language == "CSharp":
                   language = 'C#'
                if language in ['shell','json','csharp','lua','yaml','yml']:
                    print(post)
                if language in languages.keys():
                    languages[language] = languages[language] + 1
                else:
                    languages[language] = 1

    #排序后取前5种语言输出        
    languages = sorted(languages.items(), key=lambda d:d[1], reverse = True)
    return dict(languages[:6])

posts = listPosts('.\source\_posts')
languages = analyseLanguages(posts)
with open('languages.json','wt',encoding='utf-8') as f:
    f.write(json.dumps(languages))


