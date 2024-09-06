import scrapy
from scrapy.http import HtmlResponse


# scrapy crawl aop_category -O aop_categories.json
class AopCategory(scrapy.Spider):
    name = "aop_category"
    allowed_domains = ["australianorganicproducts.com.au"]
    start_urls = ["https://australianorganicproducts.com.au/"]

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
    
    def cat_filter(self, cat_str: str) -> bool:
        """
        过滤一般分类（分类```href```需以```"/collections/"```开始）
        """

        filters = {'best-sellers', 'sale', 'bulk-deals', 'clearance', 'new-organic-natural-products', 'back-in-stock'}
        return cat_str in filters

    def parse(self, response: HtmlResponse):
        cat_hrefs = [href for href in response.css('nav.site-navigation a::attr(href)').getall()
                     if href.startswith('/collections/') and (not self.cat_filter(href[13:]))]
        print(f"Total {len(cat_hrefs):_} categories".replace('_', '.'))
        
        for href in cat_hrefs:
            yield {
                "cat_url": 'https://australianorganicproducts.com.au'+href
            }
