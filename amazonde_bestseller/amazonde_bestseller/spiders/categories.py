import scrapy
from scrapy.http import HtmlResponse, Response


# scrapy crawl trendyol_categorie -O trendyol_categories.json
class TrendyolCategorie(scrapy.Spider):
    name = 'trendyol_categorie'
    allowed_domains = ['www.trendyol.com']
    start_urls = ['https://www.trendyol.com/kozmetik-x-c89']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "fr-FR,fr;q=0.8,en-GB;q=0.5,en;q=0.3",
            "Connection": "keep-alive",
            "Priority": "u=0, i",
            "Referer": "https://www.trendyol.com/",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0"
        }
    
    def start_requests(self):
        yield scrapy.Request(self.start_urls[0], headers=self.headers,
                             meta={ 'url': self.start_urls[0] },
                             callback=self.parse)
    
    def parse(self, response: HtmlResponse):
        url = response.meta['url']

        subcats = response.css('div.ctgry div[role="rowgroup"] a')
        hrefs = [sc.css('::attr(href)').get() for sc in subcats]
        subcats_links = ['https://www.trendyol.com'+href for href in hrefs if href != '/sr']

        if not subcats_links:
            yield { "cat_url": url }
        else:
            for sl in subcats_links:
                headers = { **self.headers, 'Referer': url }
                yield scrapy.Request(sl, headers=headers,
                                     meta={ 'url': sl },
                                     callback=self.parse)
