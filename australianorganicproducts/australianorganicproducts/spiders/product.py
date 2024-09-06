from json import load

import scrapy
from scrapy.http import HtmlResponse


# scrapy crawl aop_product -O aop_products.json
class AopProduct(scrapy.Spider):
    name = "aop_product"
    allowed_domains = ["australianorganicproducts.com.au"]
    start_urls = []

    CM_TO_IN = 0.393701
    G_TO_LB = 0.002205
    KG_TO_LB = 2.204623
    M_TO_IN = 39.37008
    MG_TO_LB = 0.000002

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
            # "Accept-Encoding": "gzip, deflate, br, zstd", # 若发现请求回答内容奇怪，试着不用这个请求头
            "Accept-Language": "es-ES,es;q=0.8,en-GB;q=0.5,en;q=0.3",
            "Cookie": "localization=US; cart_currency=USD",
            "Referer": "https://www.google.es",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0"
        }

        with open('aop_prod_urls.json', 'r') as f:
            produits = load(f)
        self.start_urls = [p['prod_url'] for p in produits]
        print(f'Total {len(self.start_urls):_} products'.replace("_", "."))
    
    def start_requests(self):
        for i, pu in enumerate(self.start_urls, start=1):
            print(f"{i:_}".replace('_', '.'), pu)
            yield scrapy.Request(pu, headers=self.headers, meta={ 'url': pu }, callback=self.parse)

    def parse(self, response: HtmlResponse):
        pass
