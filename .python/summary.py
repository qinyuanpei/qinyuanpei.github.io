from textrank4zh import TextRank4Keyword, TextRank4Sentence
import jieba
import logging
import frontmatter
import os
from io import BytesIO

baseDir = os.path.abspath('.')
blogDir = os.path.join(baseDir,'source\_posts')
blogFiles = os.listdir(blogDir)


def get_key_words(text, num=5):
   """提取关键词"""
   tr4w = TextRank4Keyword()
   tr4w.analyze(text, lower=True)
   key_words = tr4w.get_keywords(num)
   return [(item.word,item.weight) for item in key_words]

for blogFile in blogFiles:
    with open(os.path.join(blogDir,blogFile),'r+', encoding='utf-8') as f:
        post = frontmatter.loads(f.read())
        tr4s = TextRank4Sentence()
        tr4s.analyze(text=post.content, lower=True, source='all_filters')
        keywords = get_key_words(text=post.content,num=20)
        print(keywords)
        descriptions = [item.sentence for item in tr4s.get_key_sentences(5)]
        if len(descriptions) == 0 :
            continue
        else:
            post['description']=';'.join(descriptions)
        bytes = BytesIO()
        frontmatter.dump(post,bytes)  
        f.seek(0,0)
        f.write(bytes.getvalue().decode('utf-8'))            

def get_key_words(text, num=5):
   """提取关键词"""
   tr4w = TextRank4Keyword()
   tr4w.analyze(text, lower=True)
   key_words = tr4w.get_keywords(num)
   return [(item.word,item.weigh) for item in key_words]
##
##def get_summary(text, num=3):
##    """提取摘要"""
##    tr4s = TextRank4Sentence()
##    tr4s.analyze(text=text, lower=True, source='all_filters')
##    return [item.sentence for item in tr4s.get_key_sentences(num)]
##
##with open("C:\\Users\\admin\\Downloads\\Projects\\Blog\\source\\_posts\\邂逅AOP：说说JavaScript中的修饰器.md",encoding='utf-8') as f:
##    t = f.read();
##    #s = SnowNLP(t)
##    #print(s.keywords(5))
##    #print(s.summary(10))
##    print(get_key_words(t))
##    print(get_summary(t))


