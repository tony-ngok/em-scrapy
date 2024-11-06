import re

import scrapy
from scrapy.http import HtmlResponse


# scrapy crawl aop_prod_url
class AopProductUrl(scrapy.Spider):
    name = "aop_prod_url"
    allowed_domains = ["australianorganicproducts.com.au"]
    start_urls = []
    prod_strs = set()
    urls_output = "aop_prod_urls.txt"

    HEADERS = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.8,en-GB;q=0.5,en;q=0.3",
        "Referer": "https://australianorganicproducts.com.au/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0"
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.retry = False

        with open('aop_categories.txt', 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    self.start_urls.append(line.strip())
        print(f'Total {len(self.start_urls):_} categories'.replace("_", "."))

    def start_requests(self):
        for i, cu in enumerate(self.start_urls, start=1):
            url = "https://australianorganicproducts.com.au/collections/"+cu
            yield scrapy.Request(url, headers=self.HEADERS, callback=self.parse,
                                 cb_kwargs={ "i": i })

    def get_cat_name(self, href: str):
        cn_match = re.findall(r'/collections/([\w-]*)/products/([\w-]*)', href)
        if cn_match:
            return cn_match[0]

    def parse(self, response: HtmlResponse, i: int, actual_page: int = 1):
        print(f"{i:_}/{len(self.start_urls):_}", response.url)
        url = response.url.split("?")[0]

        prod_ax = response.css('h2.productitem--title > a::attr(href)').getall()
        for a in prod_ax:
            cat_str, prod_str = self.get_cat_name(a)
            if 'gift-card' in prod_str:
                continue
            if prod_str not in self.prod_strs:
                self.prod_strs.add(prod_str)
                self.write_url(cat_str, prod_str)

        # 翻页
        more = response.css('li.pagination--next')
        if more:
            headers = { **self.HEADERS, 'Referer': response.url }
            yield scrapy.Request(url+f'?page={actual_page+1}&grid_list=grid-view',
                                 headers=headers, callback=self.parse,
                                 cb_kwargs={ "i": i, "actual_page": actual_page+1 })

    def write_url(self, cat_str: str, prod_str: str):
        mod = 'a' if self.retry else 'w'
        with open(self.urls_output, mod, encoding='utf-8') as f_urls:
            f_urls.write(cat_str+" "+prod_str+'\n')
        if not self.retry:
            self.retry = True
