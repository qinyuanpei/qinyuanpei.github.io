﻿import os
import sys
import re
import json
import requests
import datetime

url = 'https://www.shanbay.com/api/v1/checkin/user/32365612/?page={page}'

# 扇贝打卡
def analyseCheckin(page):
    resp = requests.get(url.format(page=page))
    print(resp.content)
    obj = json.loads(resp.content)
    if obj['status_code'] == 0:
        checkins = obj['data']
        records = []
        for checkin in checkins:
            record = {}
            record['checkin_date'] = checkin['checkin_date']
            record['checkin_number'] = checkin['num_checkin_days']
            record['words'] = checkin['stats'].get('abc', {'num_today': 0, 'used_time': 0})
            record['listen'] = checkin['stats'].get('listen', {'num_today': 0, 'used_time': 0})
            record['speak'] = checkin['stats'].get('speak', {'num_today': 0, 'used_time': 0})
            record['read'] = checkin['stats'].get('read', {'num_today': 0, 'used_time': 0})
            records.append(record)
        return records
    return []

def calculateDate(months):
    pass
    

page = 1
checkins = []
pageData = analyseCheckin(page)
today = datetime.datetime.today()
begin = today - datetime.timedelta(days = 15)
while len(pageData) > 0:
    checkins.extend(pageData)
    page += 1
    pageData = analyseCheckin(page)
checkins = list(filter(lambda x:datetime.datetime.strptime(x['checkin_date'] ,'%Y-%m-%d') > begin, checkins))
if len(checkins) > 0:
    with open('shanbay.json','wt',encoding='utf-8') as f:
        f.write(json.dumps(checkins))