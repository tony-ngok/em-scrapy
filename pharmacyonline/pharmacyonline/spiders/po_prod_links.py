import json
import re

from typing import Iterable
import scrapy
from scrapy.http import HtmlResponse


# scrapy crawl po_prod_links
class PoProdLinks(scrapy.Spider):
    name = "po_prod_links"
    allowed_domains = ['www.pharmacyonline.com.au', 'aucs33.ksearchnet.com']
    start_urls = []
    urls_output = "po_prod_links.txt"

    HEADERS = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.8,en-GB;q=0.5,en;q=0.3",
        "Referer": "https://www.pharmacyonline.com.au/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0"
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.retry = False

        with open("po_cats.txt", 'r', encoding='utf-8') as f_cats:
            for line in f_cats:
                if line.strip():
                    self.start_urls.append(line.strip())

    def start_requests(self):
        for i, todo in enumerate(self.start_urls):
            yield scrapy.Request('https://www.pharmacyonline.com.au/'+todo, headers=self.HEADERS,
                                 callback=self.get_cat_str, cb_kwargs={ "i": i+1 })

    def get_cat_str(self, response: HtmlResponse, i: int):
        print(f"{i}/{len(self.start_urls)}", response.url)

        if response.status == 404:
            print("Category not found")
            return

        cat_str_sel = response.css('script#klevu_page_meta::text').get('')
        cat_name_match = re.findall(r'\"categoryName\"\s*:\s*\"([^\"]+)\"', cat_str_sel)
        if cat_name_match:
            cat_name = cat_name_match[0]
            payload = self.gen_payload(cat_name)
            yield scrapy.Request('https://aucs33.ksearchnet.com/cs/v2/search',
                                 headers=self.HEADERS,
                                 body=json.dumps(payload),
                                 callback=self.parse,
                                 method='POST',
                                 cb_kwargs={ "i": i, "cat_name": cat_name })

    def gen_payload(self, cat_name: str, p: int = 0):
        return {
            "context": {
                "apiKeys": ["klevu-172245130996617411"]
            },
            "recordQueries": [
                {
                    "id": "productList",
                    "typeOfRequest": "CATNAV",
                    "settings": {
                        "query": {
                            "term": "*",
                            "categoryPath": cat_name
                        },
                        "typeOfRecords": ["KLEVU_PRODUCT"],
                        "fields": ["1"],
                        "offset": p*100,
                        "limit": 100,
                        "typeOfSearch": "AND"
                    },
                    "filters": {
                        "filtersToReturn": {
                            "enabled": True,
                            "options": { "limit": 9999 },
                            "rangeFilterSettings": [{ "key": "klevu_price", "minMax": "true" }]
                        }
                    }
                }
            ]
        }

    def parse(self, response: HtmlResponse, i: int, cat_name: str, p: int = 0):
        print(f"{i}/{len(self.start_urls)} {cat_name} p={p}")

        if response.status == 404:
            print("Category not found")
            return
        elif response.status < 400:
            resp_info = response.json()['queryResults'][0]
            total = resp_info['meta']['totalResultsFound']
            results = resp_info['records']

            for r in results:
                prod_url = r['url'].split('/')[-1]
                prod_g = float(r.get('weight')) or 0.0
                self.write_url(prod_url, prod_g)

            if (p+1)*100 < total:
                payload = self.gen_payload(cat_name, p+1)
                yield scrapy.Request('https://aucs33.ksearchnet.com/cs/v2/search',
                                     headers=self.HEADERS,
                                     body=json.dumps(payload),
                                     callback=self.parse,
                                     method='POST',
                                     cb_kwargs={ "i": i, "cat_name": cat_name, "p": p+1 })

    def write_url(self, prod_url: str, weight_g: float = 0.0):
        mod = 'a' if self.retry else 'w'
        with open(self.urls_output, mod, encoding='utf-8') as f_urls:
            f_urls.write(prod_url)
            if weight_g:
                f_urls.write(" "+str(weight_g))
            f_urls.write('\n')
        if not self.retry:
            self.retry = True
