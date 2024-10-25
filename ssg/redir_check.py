import re
import time
from random import randint

import requests


HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "de-DE,de;q=0.9,en-GB;q=0.8,en;q=0.7",
    "connection": "keep-alive",
    "dnt": "1",
    "sec-ch-ua": '"Chromium";v="130", "Microsoft Edge";v="130", "Not?A_Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0"
}


with open('ssg_categories.txt', 'r', encoding='utf-8') as f:
    cats = [line.strip() for line in f if line.strip()]

for i, cat in enumerate(cats, start=1):
    url = 'https://www.ssg.com/disp/category.ssg?ctgId='+cat
    resp = requests.get(url, headers=HEADERS)
    print(f"{i}/{len(cats)} {resp.status_code}")

    if "location.href = '/disp/category.ssg?dispCtgId=" in resp.text:
        cat_match = re.findall(r'dispCtgId=(\d+)', resp.text)
        if cat_match:
            print(cat, "->", cat_match[0])

    time.sleep(randint(500, 1500)/1000.0)
