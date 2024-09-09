import scrapy
from scrapy.http import HtmlResponse


# scrapy crawl monotaro_category -O monotaro_categories.json
class MonotaroCategory(scrapy.Spider):
    name = "monotaro_category"
    allowed_domains = ["www.monotaro.com"]
    start_urls = ["https://www.monotaro.com/s/c-70553/", "https://www.monotaro.com/s/c-37/"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
            # "Accept-Encoding": "gzip, deflate, br, zstd", # 若发现请求回答内容奇怪，试着不用这个请求头
            "Accept-Language": "pt-PT,pt;q=0.8,en-GB;q=0.5,en;q=0.3",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0"
        }

    def start_requests(self):
        yield scrapy.Request(self.start_urls[0], headers=self.headers, meta={ 'actual_url': self.start_urls[0] }, callback=self.parse_big)
        yield scrapy.Request(self.start_urls[1], headers=self.headers, meta={ 'actual_url': self.start_urls[1] }, callback=self.parse)

    def parse_big(self, response: HtmlResponse):
        """
        进入大分类mall页面抓取
        """

        actual_url = response.meta['actual_url']

        navs = response.css('li.ChildrenCategory > a')
        for a_href in navs:
            cat_name = a_href.css('.TextLink--ChildrenCategory span.ChildrenCategory__Text::text').get().strip()
            if cat_name != '健康食品・ドリンク':
                href = a_href.css('::attr(href)').get()
                actual_url = 'https://www.monotaro.com'+href
                headers = { **self.headers, 'Referer': actual_url }
                yield scrapy.Request(actual_url, headers=headers, meta={ 'actual_url': actual_url }, callback=self.parse)

    def parse(self, response: HtmlResponse):
        actual_url = response.meta['actual_url']

        navs = response.css('nav.VisualCategoryWrap > a')
        if not navs:
            yield {
                "cat_url": actual_url
            }

        for a_href in navs:
            cat_name = a_href.css('.VisualCategoryButton span.VisualCategoryText__CategoryName::text').get().strip()
            if cat_name != 'ホワイトボード':
                href = a_href.css('::attr(href)').get()
                actual_url = 'https://www.monotaro.com'+href
                headers = { **self.headers, 'Referer': actual_url }
                yield scrapy.Request(actual_url, headers=headers, meta={ 'actual_url': actual_url }, callback=self.parse)
