import json
import re

import scrapy
from scrapy.http import HtmlResponse


# scrapy crawl trendyol_prod_url -O trendyol_prods_urls.json
class TrendyolProdUrl(scrapy.Spider):
    name = 'trendyol_prod_url'
    allowed_domains = ['www.trendyol.com', 'apigw.trendyol.com']
    start_urls = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "fr-FR,fr;q=0.8,en-GB;q=0.5,en;q=0.3",
            "Connection": "keep-alive",
            "Priority": "u=0, i",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0"
        }
    
        with open('trendyol_categories.json', 'r', encoding='utf-8') as f_in:
            self.start_urls = [cat['cat_url'] for cat in json.load(f_in)]
        print(f"Total {len(self.start_urls)} categories")

        self.prods_ids = set() # 去重用

    def start_requests(self):
        for i, url in enumerate(self.start_urls, start=1):
            headers = { **self.headers, 'Referer': url }

            cat = url.split('/')[-1]
            api_url = 'https://apigw.trendyol.com/discovery-web-searchgw-service/v2/api/infinite-scroll/'+cat+'?pi=1&channelId=1'

            print(i, api_url)
            yield scrapy.Request(api_url, headers=headers,
                                 meta={
                                     "i": i,
                                     "cat_url": url,
                                     "cat": cat,
                                     "page_no": 1
                                 },
                                 callback=self.parse)
    
    # https://apigw.trendyol.com/discovery-web-searchgw-service/v2/api/infinite-scroll/
    def parse(self, response: HtmlResponse):
        i = response.meta['i']
        cat_url = response.meta['cat_url']
        cat = response.meta['cat']
        page_no = response.meta['page_no']

        resp_json = response.json()
        resultat = resp_json['result']
        if not resultat:
            return
        
        prods = ['https://www.trendyol.com'+prod['url'] for prod in resultat['products'] if prod['cardType'] == 'PRODUCT']
        for prod in prods:
            prod_id = prod.split('-')[-1]
            if prod_id not in self.prods_ids:
                self.prods_ids.add(prod_id)
                yield { 'prod_url': prod }
        
        total_count = resultat['totalCount']

        offset_match = re.findall(r'Product_(\d+)', resultat['offsetParameters'])
        offset = int(offset_match[0]) if offset_match else total_count

        if (page_no >= 208) or (offset >= total_count):
            print(i, cat, "done")
        else:
            page_no += 1
            cat_url_pi = cat_url+f'?pi={page_no}'
            api_url_pi = 'https://apigw.trendyol.com/discovery-web-searchgw-service/v2/api/infinite-scroll/'+cat+f'?pi={page_no}&channelId=1'
            headers = { **self.headers, 'Referer': cat_url_pi }

            print(i, api_url_pi)
            yield scrapy.Request(api_url_pi, headers=headers,
                                 meta={
                                     "i": i,
                                     "cat_url": cat_url,
                                     "cat": cat,
                                     "page_no": page_no
                                 })
