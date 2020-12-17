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
            print(';'.join(descriptions))           


