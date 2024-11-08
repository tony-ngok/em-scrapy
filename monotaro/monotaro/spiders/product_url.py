import re

import scrapy
from scrapy.http import HtmlResponse


# scrapy crawl monotaro_prod_url
class MonotaroProductUrl(scrapy.Spider):
    name = "monotaro_prod_url"
    allowed_domains = ["www.monotaro.com"]
    start_urls = []
    urls_output = "monotaro_prod_urls.txt"

    # https://docs.scrapy.org/en/2.11/topics/settings.html?highlight=retrymiddleware
    # https://docs.scrapy.org/en/2.11/topics/downloader-middleware.html#std-reqmeta-dont_redirect
    handle_httpstatus_list = [301, 302, 404]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.retry = False
        self.prod_nos = set()

        with open('monotaro_cats.txt', 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    self.start_urls.append(line.strip())
        print(f'Total {len(self.start_urls):_} categories'.replace("_", "."))

    def get_headers(self, referer: str):
        return {
            "Accept": "*/*",
            "Accept-Language": "pt-PT,pt;q=0.8,en-GB;q=0.5,en;q=0.3",
            "Content-Type": "application/json",
            "Referer": referer,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0"
        }

    def get_url(self, cat_no: str, p: int = 1):
        if p > 1:
            return f'https://www.monotaro.com/s/c-{cat_no}/page-{p}/?abolition=1'
        return f'https://www.monotaro.com/s/c-{cat_no}/?abolition=1'

    def get_no(self, href: str):
        catno_match = re.findall(r'/g/(\d+)', href)
        if catno_match:
            return catno_match[0]

    def start_requests(self):
        for i, cat_no in enumerate(self.start_urls):
            url = self.get_url(cat_no)
            yield scrapy.Request(url, headers=self.get_headers(cat_no),
                                 meta={ 'cookiejar': i },
                                 callback=self.parse,
                                 cb_kwargs={ "i": i+1, "cat_no": cat_no })

    def parse(self, response: HtmlResponse, i: int, cat_no: str, p: int = 1):
        print(f"{i:_}/{len(self.start_urls):_}".replace('_', '.'), response.url)

        prod_ax = response.css('div.SearchResultProductColumn')
        for a in prod_ax:
            img = a.css('div.SearchResultProductColumn__LeftColumn img::attr(data-rep-img-src)').get('')
            nomore = a.css('div.SearchResultProductColumn__RightColumn span[title="取扱い終了"]')

            if img and (not (('mono_image_na' in img) or nomore)): # 没有画像和彻底断货的商品无法卖
                href = a.css('div.SearchResultProductColumn__LeftColumn > a::attr(href)').get()
                if href not in self.prod_nos:
                    prod_no = self.get_no(href)
                    self.prod_nos.add(prod_no)
                    self.write_prod(prod_no)

        next_a = response.css('a.Button--PaginationNext').get()
        if next_a:
            next_url = self.get_url(cat_no, p+1)
            yield scrapy.Request(next_url, headers=self.get_headers(response.url),
                                 meta={ 'cookiejar': response.meta['cookiejar'] },
                                 callback=self.parse,
                                 cb_kwargs={ "i": i, "cat_no": cat_no, "p": p+1 })

    def write_prod(self, prod: str):
        mod = 'a' if self.retry else 'w'
        with open(self.urls_output, mod, encoding='utf-8') as f_urls:
            f_urls.write(prod+'\n')
        if not self.retry:
            self.retry = True
