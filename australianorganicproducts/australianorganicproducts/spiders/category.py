import re

import scrapy
from scrapy.http import HtmlResponse


# scrapy crawl aop_category
class AopCategory(scrapy.Spider):
    name = "aop_category"
    allowed_domains = ["australianorganicproducts.com.au"]
    start_urls = ["https://australianorganicproducts.com.au/"]
    cats_output = "aop_categories.txt"

    HEADERS = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.8,en-GB;q=0.5,en;q=0.3",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0"
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.retry = False

    def start_requests(self):
        yield scrapy.Request(self.start_urls[0], headers=self.HEADERS, callback=self.parse)

    def get_cat(self, href: str):
        cat_match = re.findall(r'/collections/([\w-]*)', href)
        if cat_match:
            return cat_match[0]

    def cat_filter(self, cat_str: str) -> bool:
        """
        过滤一般分类（分类```href```需以```/collections/```开始）
        """

        filters = {'best-sellers', 'sale', 'bulk-deals', 'clearance', 'new-organic-natural-products', 'back-in-stock'}
        return cat_str in filters

    def parse(self, response: HtmlResponse):
        cat_hrefs = [href for href in response.css('nav.site-navigation a::attr(href)').getall() if href.startswith('/collections/')]
        cats = [self.get_cat(href) for href in cat_hrefs if not self.cat_filter(self.get_cat(href))]
        print(f"Total {len(cats):_} categories".replace('_', '.'))

        for cat in cats:
            self.write_cat(cat)

    def write_cat(self, cat: str):
        mod = 'a' if self.retry else 'w'
        with open(self.cats_output, mod, encoding='utf-8') as f_cats:
            f_cats.write(cat+'\n')
        if not self.retry:
            self.retry = True
