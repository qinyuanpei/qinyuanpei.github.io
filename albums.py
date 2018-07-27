#! python3
# -*- coding: utf-8 -*-
import os
import re
import sys
import uuid
import json
import pytz
import shutil
import datetime
from PIL import Image
from itertools import groupby
from qiniu import Auth, put_file, etag
import qiniu.config


class ImageProcessor:

    def __init__(self):
        self.workspace = os.path.abspath('.')
        self.albums_json = os.path.join(self.workspace, 'albums.json')
        self.albums_folder = os.path.join(self.workspace, 'albums')
        self.qiniu_URLPerfix = 'http://7wy477.com1.z0.glb.clouddn.com'
        self.qiniu_accessKey = 'n_Xh-4hMbR-kc2ad424fN0v3YCsqoD_zApWpg4Bo'
        self.qiniu_secretKey = 'GZqa-JzynnnbCe_-q-AIDir1c8d_Jrk1lbVOKEU2'
        self.qiniu_bucketName = 'blogspace'

    def loadImages(self, filePath):
        images = []
        assetFiles = os.listdir(filePath)
        assetFiles = list(map(lambda x: os.path.join(filePath, x), assetFiles))
        for assetFile in assetFiles:
            assetFile = assetFile
            if(os.path.isfile(assetFile)):
                images.append(assetFile)
            else:
                images.extend(self.loadImages(assetFile))
        return images

    def handleImage(self, filePath):
        IMG = Image.open(filePath)
        IMG = self.cropImage(IMG)
        IMG = self.compressImage(IMG)
        IMG = IMG.convert('RGB')

        # upload origin image
        item = {}
        (w, h) = IMG.size
        item['size'] = {'width': w, 'height': h}
        fileName = os.path.basename(filePath)
        folder = os.path.dirname(filePath)
        item['month'] = os.path.basename(folder)
        item['year'] = os.path.basename(os.path.dirname(folder))
        item['origin'] = self.uploadImage(filePath)

        # create thumb image and upload
        array = os.path.splitext(fileName)
        newFile = '{0}-thumb{1}'.format(array[0], array[1])
        thumbFile = os.path.join(self.albums_folder, newFile)
        if(not os.path.exists(os.path.dirname(thumbFile))):
            os.mkdir(os.path.dirname(thumbFile))
        IMG.save(thumbFile)
        item['thumb'] = self.uploadImage(thumbFile)

        # comment is optional
        item['comment'] = ''
        return item

    def handleImages(self):
        albums = []
        if(os.path.exists(self.albums_json)):
            with open(self.albums_json, "rt", encoding="UTF-8") as f_dump:
                ambums = json.load(f_dump)

        files = self.loadImages(self.albums_folder)
        if(len(files) <= 0):
            return

        # Generate JSON
        items = list(map(lambda x: self.handleImage(x), files))
        groups = groupby(
            items, key=lambda x: '{0},{1}'.format(x['year'], x['month']))
        for (key, group) in groups:
            if(self.hasAlbum(key, albums)):
                self.updateAlbum(key, albums, list(group))
            else:
                albums.append({
                    'year': key.split(',')[0],
                    'month': key.split(',')[1],
                    'images': list(group)
                })

        with open(self.albums_json, "wt", encoding="UTF-8") as f_dump:
            json.dump(albums, f_dump, ensure_ascii=False)

        # Clean Albums
        self.cleanAlbums()

    def cropImage(self, srcImage):
        (x, y) = srcImage.size
        if x > y:
            region = (int(x/2-y/2), 0, int(x/2+y/2), y)
        elif x < y:
            region = (0, int(y/2-x/2), x, int(y/2+x/2))
        else:
            region = (0, 0, x, y)

        destImage = srcImage.crop(region)
        return destImage

    def compressImage(self, srcImage, scale=2):
        (w, h) = srcImage.size
        srcImage.thumbnail((int(w/scale), int(h/scale)))
        return srcImage

    def uploadImage(self, srcImage):
        q = Auth(self.qiniu_accessKey, self.qiniu_secretKey)
        fileName = os.path.basename(srcImage)
        token = q.upload_token(self.qiniu_bucketName, fileName, 3600)
        ret, resp = put_file(token, fileName, srcImage)
        if(resp.status_code == 200):
            os.remove(srcImage)
            return '{0}\{1}'.format(self.qiniu_URLPerfix, fileName)
        return None

    def cleanAlbums(self):
        files = os.listdir(self.albums_folder)
        for file in files:
            filePath = os.path.join(self.albums_folder, file)
            if(os.path.isdir(filePath)):
                if(len(self.loadImages(filePath)) <= 0):
                    shutil.rmtree(filePath)
            else:
                os.remove(filePath)

    def hasAlbum(self, key, albums):
        year = key.split(',')[0]
        month = key.split(',')[1]
        return len(list(filter(lambda x: x['year'] == year and x['month'] == month, albums))) > 0

    def updateAlbum(self, key, albums, images):
        year = key.split(',')[0]
        month = key.split(',')[1]
        for album in albums:
            if(album['month'] == month and album['year'] == year):
                album.images.extend(images)
                break


if(__name__ == '__main__'):
    handler = ImageProcessor()
    handler.handleImages()
