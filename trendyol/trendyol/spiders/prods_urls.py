import re

import scrapy
from scrapy.http import HtmlResponse


# scrapy crawl trendyol_prod_url
class TrendyolProdUrl(scrapy.Spider):
    name = 'trendyol_prod_url'
    allowed_domains = ['apigw.trendyol.com']
    start_urls = []
    urls_output = "trendyol_prods_urls.txt"

    HEADERS = {
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prods_ids = set() # 去重用
        self.retry = False

        with open('trendyol_categories.txt', 'r', encoding='utf-8') as f_in:
            for line in f_in:
                if line.strip():
                    self.start_urls.append(line.strip())
        print(f"Total {len(self.start_urls)} categories")

    def gen_api(self, cat: str, pi: int = 1):
        return f'https://apigw.trendyol.com/discovery-web-searchgw-service/v2/api/infinite-scroll/{cat}?pi={pi}&channelId=1'

    def start_requests(self):
        for i, cat in enumerate(self.start_urls):
            api_url = self.gen_api(cat)
            yield scrapy.Request(api_url, headers=self.HEADERS,
                                 meta={ "cookiejar": i },
                                 callback=self.parse,
                                 cb_kwargs={ "i": i+1, "cat": cat })

    def parse(self, response: HtmlResponse, i: int, cat: str, pi: int = 1):
        print(f"{i:_}/{len(self.start_urls):_}", response.url)
        if response.status == 404:
            print("Categorie not found")
            return

        resp_json = response.json()
        resultat = resp_json['result']
        if not resultat:
            print("Empty categorie")
            return

        prods = ['https://www.trendyol.com'+prod['url'] for prod in resultat['products'] if prod['cardType'] == 'PRODUCT']
        for prod in prods:
            prod_id = prod.split('-')[-1]
            if prod_id not in self.prods_ids:
                self.prods_ids.add(prod_id)
                self.write_url(prod_id)

        total_count = resultat['totalCount']
        offset_match = re.findall(r'Product_(\d+)', resultat['offsetParameters'])
        offset = int(offset_match[0]) if offset_match else total_count

        if (pi >= 208) or (offset >= total_count):
            print(i, cat, "done")
        else:
            pi += 1
            api_url_pi = self.gen_api(cat, pi+1)

            print(i, api_url_pi)
            yield scrapy.Request(api_url_pi, headers=self.HEADERS,
                                 meta={ "cookiejar": response.meta['cookiejar'] },
                                 callback=self.parse,
                                 cb_kwargs={ "i": i, "cat": cat, "pi": pi+1 })

    def write_url(self, cat: str):
        mod = 'a' if self.retry else 'w'
        with open(self.urls_output, mod, encoding='utf-8') as f_urls:
            f_urls.write(cat+'\n')
        if not self.retry:
            self.retry = True
