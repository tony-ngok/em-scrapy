import scrapy
from scrapy.http import HtmlResponse


# scrapy crawl aop_category -O aop_categories.json
class AopCategory(scrapy.Spider):
    name = "aop_category"
    allowed_domains = ["australianorganicproducts.com.au"]
    start_urls = ["https://australianorganicproducts.com.au/collections"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
            # "Accept-Encoding": "gzip, deflate, br, zstd", # 若发现请求回答内容奇怪，试着不用这个请求头
            "Accept-Language": "es-ES,es;q=0.8,en-GB;q=0.5,en;q=0.3",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0"
        }

    def start_requests(self):
        yield scrapy.Request(self.start_urls[0], headers=self.headers, callback=self.parse)
    
    def parse(self, response: HtmlResponse):
        pass
