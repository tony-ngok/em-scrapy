import os
import re

import scrapy
from scrapy.http import HtmlResponse


class SsgProdsUrls(scrapy.Spider):
    name = "ssg_prod_url"
    allowed_domains = ["www.ssg.com"]

    custom_settings = {
        'DOWNLOAD_DELAY': 0.2,
        'DOWNLOADER_MIDDLEWARES': { # 每发送请求后，先经过中间件返回回答，然后将回答通过回调函数处理
            'ssg.middlewares.SsgProdsIdsErrsMiddleware': 543
        }
    }

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

    def __init__(self, start_urls: list[str] = [], retry: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = start_urls if retry else None
        self.output_file = "ssg_prods_urls.txt"

        self.prevs = None
        if retry: # 重试模式
            print("Retry mode")

            if os.path.exists(self.output_file): # 以前收集到的数据，用于去重
                with open(self.output_file, 'r', encoding='utf-8') as f_output:
                    self.prevs = { line.strip(): True for line in f_output if line.strip() }
                open(self.output_file, 'w').close()
            else: # 以前没有收集到数据
                print("Data file not found:", self.output_file)
        else: # 从头开始
            print("Start anew")
            open(self.output_file, 'w').close()

            cats_file = "ssg_categories.txt"
            if os.path.exists(cats_file): # 从分类中读取要做的
                with open(cats_file, 'r', encoding='utf-8') as f_cats:
                    self.start_urls = [line.strip() for line in f_cats if line.strip()]
            else:
                print("Categories files not found:", cats_file)

        self.prods_count = len(self.prevs) if self.prevs else 0

    def start_requests(self):
        for i, url in enumerate(self.start_urls):
            url = self.page_url('tgId='+url) # 分类号 -> URL
            headers = { **self.HEADERS, 'referer': 'https://www.ssg.com/monm/main.ssg' }
            yield scrapy.Request(url, headers=headers,
                                 meta={ "cookiejar": i },
                                 callback=self.parse,
                                 cb_kwargs={ "i": i+1 })

    def page_url(self, url: str, p: int = 1):
        cat_match = re.findall(r'tgId=(\d+)', url)
        if cat_match:
            return f'https://www.ssg.com/disp/category.ssg?pageSize=100&dispCtgId={cat_match[0]}&page={p}'

    def parse(self, response: HtmlResponse, i: int, p: int = 1, cat_prod_count: int = 0):
        print(f"{i:_}/{len(self.start_urls):_}".replace("_", "."), response.request.url)

        items = response.css('li[data-unittype="item"]')
        for item in items:
            print([items.css('::attr(data-advertbilngtypecd)').get()])
            if not items.css('::attr(data-advertbilngtypecd)').get(): # 过滤掉广告类商品
                prod_id = item.css(':scope div.ssgitem_detail > a::attr(data-info)').get()
                if prod_id:
                    with open(self.output_file, 'a', encoding="utf-8") as f_out:
                        f_out.write(prod_id+'\n')
                        cat_prod_count += 1
                        self.prods_count += 1
        
        next_p = response.css('a.btn_next')
        if next_p or (p < len(response.css('div.com_paginate > *'))): # 总10页以内的分类没有翻页按钮
            headers = { **self.HEADERS, 'referer': response.url }
            next_url = self.page_url(response.request.url, p+1)
            yield scrapy.Request(next_url, headers=headers,
                                 meta={ "cookiejar": response.meta["cookiejar"] },
                                 callback=self.parse,
                                 cb_kwargs={ "i": i, "p": p+1, "cat_prod_count": cat_prod_count })
        else:
            print(f"{i:_}/{len(self.start_urls):_}".replace("_", "."), f"Total {cat_prod_count:_} product(s)".replace("_", "."))
            print(f"Total {self.prods_count:_} product(s)".replace("_", "."))
