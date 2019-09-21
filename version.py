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

with open('VERSION.txt','r', encoding='utf-8') as f_ver:
    version = f_ver.readlines()[0]
    with open('_config.yml', 'r+', encoding='utf-8') as f_conf:
        conf = yaml.load(f_conf)
        conf['version'] = version
        yaml.dump(conf, f_conf)