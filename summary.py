from textrank4zh import TextRank4Keyword, TextRank4Sentence
import jieba
import json
import jieba.analyse
import logging
import frontmatter
import os
from io import BytesIO

baseDir = os.path.abspath('.')
blogDir = os.path.join(baseDir,'source\_posts')
dataDir = os.path.join(baseDir,'source\_data')
blogFiles = os.listdir(blogDir)


def extract_tags(text, top=5):
   tr4w = TextRank4Keyword()
   tr4w.analyze(text, lower=True)
   key_words = tr4w.get_keywords(top)
   print(jieba.analyse.textrank(text, topK=20, withWeight=False, allowPOS=('ns', 'n', 'vn', 'v')))
   return [(item.word,item.weight) for item in key_words]

def extract_summaries(text, top=5):
    tr4s = TextRank4Sentence()
    tr4s.analyze(text=text, lower=True, source='all_filters')
    return [item.sentence for item in tr4s.get_key_sentences(5)]

summaries = {}
for blogFile in blogFiles:
    with open(os.path.join(blogDir,blogFile),'r+', encoding='utf-8') as f:
        post = frontmatter.loads(f.read())
        summary = {}
        abbrlink = post['abbrlink']
        tags = extract_tags(post.content)
        descs = extract_summaries(post.content)
        if len(descs) == 0:
            summary['descs'] = ''
        else:
            summary['descs'] = ';'.join(descs)  
        if len(tags) == 0:
            summary['tags'] = []
        else:
            summary['tags'] = tags
        summary['title'] = post['title']
        summaries[abbrlink] = summary
        print(summary)
        
with open(os.path.join(dataDir, 'summaries.json'), 'wt', encoding='utf-8') as fp:
    json.dump(summaries, fp)   


