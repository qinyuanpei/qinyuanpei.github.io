#! python3
# -*- coding: utf-8 -*-
import os
import re
import sys
import json
import pytz
import datetime
from PIL import Image
from itertools import groupby

class ImageProcessor:

    def __init__(self):
        self.workspace = os.path.abspath('.')
        self.origin_folder = os.path.join(self.workspace,'albums/origin/')
        self.thumb_folder = os.path.join(self.workspace,'albums/thumb/')
        # self.assets_perfix = 'https://github.com/qinyuanpei/qinyuanpei.github.io/blob/blog/'
        self.assets_perfix ='/assets/'
    
    def loadImages(self,filePath):
        images = []
        assetFiles = os.listdir(filePath)
        assetFiles = list(map(lambda x:os.path.join(filePath,x),assetFiles))
        for assetFile in assetFiles:
            assetFile = assetFile
            if(os.path.isfile(assetFile)):
                images.append(assetFile)
            else:
                images.extend(self.loadImages(assetFile))
        return images

    def handleImage(self,filePath):
        IMG = Image.open(filePath)
        IMG = self.cropImage(IMG)
        IMG = self.compressImage(IMG)
        IMG = IMG.convert('RGB')
       
        item = {}
        (w,h) = IMG.size
        item['size'] = {'width':w,'height':h}
        fileName = os.path.basename(filePath)
        folder = os.path.dirname(filePath)
        item['month'] = os.path.basename(folder)
        item['year'] = os.path.basename(os.path.dirname(folder))
        item['origin'] = '{0}/albums/origin/{1}/{2}/{3}'.format(
            self.assets_perfix,item['year'],item['month'],fileName
        )
        item['thumb'] = '{0}/albums/thumb/{1}/{2}/{3}'.format(
            self.assets_perfix,item['year'],item['month'],fileName
        )
        item['comment'] = ''
        thumbFile = item['thumb'].replace(self.assets_perfix,self.workspace)
        if(not os.path.exists(os.path.dirname(thumbFile))):
            os.mkdir(os.path.dirname(thumbFile))
        IMG.save(thumbFile)
        return item
        

    def handleImages(self):
        albums = []
        files = self.loadImages(self.origin_folder)
        items = list(map(lambda x:self.handleImage(x),files))
        groups = groupby(items,key=lambda x:'{0},{1}'.format(x['year'],x['month']))
        for (key,group) in groups:
            albums.append({
                    'year':key.split(',')[0],
                    'month':key.split(',')[1],
                    'images':list(group)
            })
        
        with open("albums.json", "w", encoding="UTF-8") as f_dump:
            json.dump(albums, f_dump, ensure_ascii=False)


    def cropImage(self,srcImage):
        (x, y) = srcImage.size  
        if x > y:  
            region = (int(x/2-y/2), 0, int(x/2+y/2), y)  
        elif x < y:  
            region = (0, int(y/2-x/2), x, int(y/2+x/2))  
        else:  
            region = (0, 0, x, y)  

        destImage = srcImage.crop(region)
        return destImage

    def compressImage(self,srcImage,scale = 2):
        (w,h) = srcImage.size
        srcImage.thumbnail((int(w/scale), int(h/scale)))
        return srcImage

if(__name__ == '__main__'):
    handler = ImageProcessor()
    handler.handleImages()