from json import load

import scrapy
from scrapy.http import HtmlResponse


# scrapy crawl monotaro_prod_url -O monotaro_prod_urls.json
class MonotaroProductUrl(scrapy.Spider):
    name = "monotaro_prod_url"
    allowed_domains = ["www.monotaro.com"]
    start_urls = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prod_hrefs = set()

        with open('monotaro_categories.json', 'r') as f:
            categories = load(f)
        self.start_urls = [c['cat_url'] for c in categories]
        print(f'Total {len(self.start_urls):_} categories'.replace("_", "."))

    def get_headers(self, referer: str):
        return {
            "Accept": "*/*",
            # "Accept-Encoding": "gzip, deflate, br, zstd", # 若发现请求回答内容奇怪，试着不用这个请求头
            "Accept-Language": "pt-PT,pt;q=0.8,en-GB;q=0.5,en;q=0.3",
            "Content-Type": "application/json",
            "Referer": referer,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0"
        }
    
    def start_requests(self):
        # self.start_urls = ['https://www.monotaro.com/s/c-105779/', 'https://www.monotaro.com/s/c-134918/'] # test
        for i, cu in enumerate(self.start_urls, start=1):
            print(f"{i:_}".replace('_', '.'), cu)
            yield scrapy.Request(cu, headers=self.get_headers(cu),
                                 meta={
                                     'cat_url': cu,
                                     'page': 1
                                     },
                                 callback=self.parse)

    def parse(self, response: HtmlResponse):
        cu = response.meta['cat_url']
        page = response.meta['page']

        prod_ax = response.css('div.SearchResultProductColumn')
        for a in prod_ax:
            img = a.css('div.SearchResultProductColumn__LeftColumn img::attr(data-rep-img-src)').get()
            nomore = a.css('div.SearchResultProductColumn__RightColumn span[title="取扱い終了"]')

            if not (('mono_image_na' in img) or nomore): # 没有画像和彻底断货的商品无法卖
                href = a.css('div.SearchResultProductColumn__LeftColumn > a::attr(href)').get()
                if href not in self.prod_hrefs:
                    self.prod_hrefs.add(href)
                    yield {
                        "prod_url": 'https://www.monotaro.com'+a.css('::attr(href)').get()
                    }
        
        next_a = response.css('a.Button--PaginationNext').get()
        if next_a:
            page += 1
            yield scrapy.Request(cu+f'page-{page}/', headers=self.get_headers(response.url),
                                 meta={
                                     'cat_url': cu,
                                     'page': page
                                     },
                                 callback=self.parse)

    def closed(self, reason):
        # print(self.prod_ids)
        print(f"{len(self.prod_hrefs):_} unique products".replace('_', '.'))
