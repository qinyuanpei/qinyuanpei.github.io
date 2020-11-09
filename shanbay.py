import os
import sys
import re
import json
import requests

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
            record['words'] = checkin['stats']['bdc']
            record['listen'] = checkin['stats']['listen']
            records.append(record)
        return records
    return []

page = 1
checkins = []
pageData = analyseCheckin(page)
while len(pageData) > 0:
    checkins.extend(pageData)
    page += 1
    pageData = analyseCheckin(page)
if len(checkins) > 0:
    with open('shanbay.json','wt',encoding='utf-8') as f:
        f.write(json.dumps(checkins))