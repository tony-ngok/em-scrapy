import scrapy
from scrapy.http import HtmlResponse


# scrapy crawl po_cats -O po_cats.json
class POCategories(scrapy.Spider):
    """
    首页子分类内容为传统HTML，因此可直接用Scrapy抓取
    """
    
    name = "po_cats"
    allowed_domains = ['www.pharmacyonline.com.au']
    start_urls = ['https://www.pharmacyonline.com.au/']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br, zstd", # 若发现请求回答内容奇怪，试着不用这个请求头
            "Accept-Language": "es-ES,es;q=0.8,en-GB;q=0.5,en;q=0.3",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0"
        }
    
    def start_requests(self):
        yield scrapy.Request(self.start_urls[0], headers=self.headers, callback=self.parse)

    def parse(self, response: HtmlResponse):
        l_items = response.css('li[data-title="Shop by category"] li.item > a::attr(href)').getall()
        parx = set(response.css('li[data-title="Shop by category"] li.item.-parent > a::attr(href)').getall())
        l_cats = [l for l in l_items if l not in parx]

        for l in l_cats:
            yield {
                "cat_link": l
            }

    def write_cat(self, cat_no: str):
        pass
