import json

import requests
import scrapy
from scrapy.http import HtmlResponse


# scrapy crawl trendyol_prod_url -O trendyol_prods_urls.json
class TrendyolProdUrl(scrapy.Spider):
    name = 'trendyol_prod_url'
    allowed_domains = ['www.trendyol.com']
    start_urls = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "fr-FR,fr;q=0.8,en-GB;q=0.5,en;q=0.3",
            "Connection": "keep-alive",
            "Priority": "u=0, i",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0"
        }
    
    
