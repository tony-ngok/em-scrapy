# 有些文字描述没抓到的要重新抓

import json
import os
import time
from random import randint

import requests
from scrapy.http import HtmlResponse


HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "de-DE,de;q=0.9,en-GB;q=0.8,en;q=0.7",
    "dnt": "1",
    "priority": "u=0, i",
    "referer": "https://shopping.naver.com/",
    "sec-ch-ua": "\"Microsoft Edge\";v=\"129\", \"Not=A?Brand\";v=\"8\", \"Chromium\";v=\"129\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Yeti/1.1; +https://naver.me/spd) Chrome/106.0.5249.0 Safari/537.36"
}

DESC_IMG_FILTER = [
    "%EC%BF%A0%ED%8F%B0", "%ED%95%A0%EC%9D%B8", "%EC%8A%88%ED%8D%BC%EB%94%9C",
    "%EB%B0%B0%EB%84%88", "%EC%95%88%EB%82%B4", "%EB%B0%B0%EC%86%A1",
    "%EA%B3%B5%EC%8B%9D", "%EC%9D%B8%ED%8A%B8%EB%A1%9C", "%ED%95%98%EB%8B%A8",
    "%EB%AA%A8%EB%93%A0%EC%A0%9C%ED%92%88"
]


def get_descr(prod_id: str):
    desc_url = f'https://shopping.naver.com/product-detail/v1/products/{prod_id}/contents/pc/PC'
    descr = ""

    j = 1
    descr_resp = requests.get(desc_url, headers=HEADERS, timeout=60, allow_redirects=False)
    while descr_resp.status_code >= 300:
        if descr_resp.status_code == 404:
            print("No div descriptions")
            return ""
        else:
            print(f"API call fail with status {descr_resp.status_code}: {desc_url} ({j}/100)")
            j += 1
            if j >= 100:
                raise Exception(f'Status {descr_resp.status_code}')
            time.sleep(randint(2400, 4800)/1000.0)
            descr_resp = requests.get(desc_url, headers=HEADERS, timeout=60, allow_redirects=False)
    if descr_resp.status_code == 204:
        print("No div descriptions")
        return ""

    raw_descr = descr_resp.json()['renderContent']
    resp_tmp = HtmlResponse('', body=raw_descr, encoding='utf-8')
    resp_getall = resp_tmp.css('p > span, img')

    for sel in resp_getall:
        if sel.root.tag == 'span':
            span_txt = " ".join(sel.css('::text').get().replace("\n", "").strip().split())
            descr += f'<p>{span_txt}</p>'
        else:
            img_url = sel.css('::attr(data-src)').get()
            if not img_url:
                continue

            filter = False
            for f in DESC_IMG_FILTER:
                if f in img_url:
                    filter = True
                    break
            if not filter:
                descr += f'<p><img src="{img_url}"></p>'

    return (f'<div class="naver-handmade-descr">{descr}</div>' if descr else "")


if __name__ == '__main__':
    try:
        with open('naver_handmade_prods.txt', 'r', encoding='utf-8') as f_orig, open('prods_temp', 'w', encoding='utf-8') as f_new:
            for line in f_orig:
                data = json.loads(line[:-1])
                prod_id = data['prod_id']
                descr = data['description']

                if not descr:
                    got_descr = get_descr(prod_id)
                    data['description'] = (got_descr if got_descr else None)
                elif not (descr.startswith('<div ')):
                    data['description'] = get_descr(prod_id)+descr

                json.dump(data, f_new, ensure_ascii=False)
                f_new.write(',\n')
                time.sleep(randint(2400, 4800)/1000.0)

            os.remove("naver_handmade_prods.txt")
            os.rename('prods_temp', "naver_handmade_prods.txt")
    except Exception as e:
        print("ERROR:", str(e))
