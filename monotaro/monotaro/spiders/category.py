import re

import scrapy
from scrapy.http import HtmlResponse


# scrapy crawl monotaro_category
class MonotaroCategory(scrapy.Spider):
    name = "monotaro_category"
    allowed_domains = ["www.monotaro.com"]
    start_urls = ["https://www.monotaro.com/s/c-70553/", "https://www.monotaro.com/s/c-37/"]
    cats_output = "monotaro_cats.txt"

    HEADERS = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
        "Accept-Language": "pt-PT,pt;q=0.8,en-GB;q=0.5,en;q=0.3",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0"
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cats = set()
        self.retry = False

    def get_cat(self, url: str):
        cat_match = re.findall(r'/c-(\d+)', url)
        if cat_match:
            return cat_match[0]

    def start_requests(self):
        yield scrapy.Request(self.start_urls[0], headers=self.HEADERS, callback=self.parse_big,
        meta={
            'dont_redirect': True,
            'handle_httpstatus_list': [301, 404]
            })
        yield scrapy.Request(self.start_urls[1], headers=self.HEADERS, callback=self.parse,
        meta={
            'dont_redirect': True,
            'handle_httpstatus_list': [301, 404]
            })

    def parse_big(self, response: HtmlResponse):
        """
        进入大分类mall页面抓取
        """

        navs = response.css('li.ChildrenCategory > a')
        for a_href in navs:
            cat_name = a_href.css('.TextLink--ChildrenCategory span.ChildrenCategory__Text::text').get().strip()
            if cat_name != '健康食品・ドリンク':
                href = a_href.css('::attr(href)').get()
                next_url = 'https://www.monotaro.com'+href
                headers = { **self.HEADERS, 'Referer': next_url }
                yield scrapy.Request(next_url, headers=headers, callback=self.parse,
                                     meta={
                                        'dont_redirect': True, # https://stackoverflow.com/questions/15476587/scrapy-how-to-stop-redirect-302
                                        'handle_httpstatus_list': [301, 404]
                                     })

    def parse(self, response: HtmlResponse):
        if response.status == 404:
            print("Category not found", response.url)
            return

        navs = response.css('nav.VisualCategoryWrap > a')
        if not navs:
            cat_no = self.get_cat(response.url)
            if cat_no not in self.cats:
                self.cats.add(cat_no)
                self.write_cat(cat_no)

        for a_href in navs:
            cat_name = a_href.css('.VisualCategoryButton span.VisualCategoryText__CategoryName::text').get().strip()
            if cat_name != 'ホワイトボード':
                href = a_href.css('::attr(href)').get('')
                next_url = 'https://www.monotaro.com'+href
                headers = { **self.HEADERS, 'Referer': response.url }
                yield scrapy.Request(next_url, headers=headers, callback=self.parse,
                                     meta={
                                        'dont_redirect': True,
                                        'handle_httpstatus_list': [301, 404]
                                     })

    def write_cat(self, cat_no: str):
        mod = 'a' if self.retry else 'w'
        with open(self.cats_output, mod, encoding='utf-8') as f_cats:
            f_cats.write(cat_no+'\n')
        if not self.retry:
            self.retry = True
