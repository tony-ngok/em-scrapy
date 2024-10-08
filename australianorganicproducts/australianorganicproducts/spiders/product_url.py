from json import load, loads
from re import findall

import scrapy
from scrapy.http import HtmlResponse


# scrapy crawl aop_prod_url -O aop_prod_urls.json
class AopProductUrl(scrapy.Spider):
    name = "aop_prod_url"
    allowed_domains = ["australianorganicproducts.com.au"]
    start_urls = []
    prod_strs = set()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
            # "Accept-Encoding": "gzip, deflate, br, zstd", # 若发现请求回答内容奇怪，试着不用这个请求头
            "Accept-Language": "es-ES,es;q=0.8,en-GB;q=0.5,en;q=0.3",
            "Referer": "https://australianorganicproducts.com.au/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0"
        }

        with open('aop_categories.json', 'r') as f:
            categories = load(f)
        self.start_urls = [c['cat_url'] for c in categories]
        print(f'Total {len(self.start_urls):_} categories'.replace("_", "."))

    def start_requests(self):
        # self.start_urls = ['https://australianorganicproducts.com.au/collections/gift-ideas'] # test
        for i, cu in enumerate(self.start_urls, start=1):
            print(f"{i:_}".replace('_', '.'), cu)
            yield scrapy.Request(cu, headers=self.headers,
                                 meta={
                                     'cat_url': cu,
                                     'actual_page': 1,
                                     'page_count': None
                                     },
                                 callback=self.parse)

    def parse(self, response: HtmlResponse):
        cu = response.meta['cat_url']
        actual_page = response.meta['actual_page']
        page_count = response.meta['page_count']
        
        # 获取分类最大翻页数
        if page_count is None:
            scr_count_text = response.css('script[data-section-type="static-collection-faceted-filters"]::text').get()
            sp_match = findall(r'"product_count"\s*:\s*(\d+),', scr_count_text)
            if sp_match:
                page_count = -(int(sp_match[0]) // -24)
        if not page_count:
            return
        print(cu, f"({actual_page:_}/{page_count:_})".replace("_", "."))

        prod_ax = response.css('h2.productitem--title > a::attr(href)').getall()
        for a in prod_ax:
            prod_str = a.split('/')[-1]
            if 'gift-card' in prod_str:
                continue
            
            if prod_str not in self.prod_strs:
                self.prod_strs.add(prod_str)
                yield {
                    "prod_url": 'https://australianorganicproducts.com.au'+a
                }

        # 翻页
        if actual_page < page_count:
            self.headers['Referer'] = response.url
            yield scrapy.Request(cu+f'?page={actual_page}&grid_list=grid-view',
                                 headers=self.headers,
                                 meta={
                                     'cat_url': cu,
                                     'actual_page': actual_page+1,
                                     'page_count': page_count
                                     },
                                 callback=self.parse)

    def closed(self, reason):
        # print(self.prod_strs)
        print(f"{len(self.prod_strs):_} unique products".replace('_', '.'))
