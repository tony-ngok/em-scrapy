import gzip
import io
import xml.etree.ElementTree as ET

import scrapy
from scrapy.http import HtmlResponse, TextResponse


# scrapy crawl product-url -O apodiscounter_produkturls.json
class ProductUrlSpider(scrapy.Spider):
    name = "product-url"
    allowed_domains = ["apodiscounter.de"]

    # 来源：https://apodiscounter.de/sitemapindex.xml
    start_urls = ["https://www.apodiscounter.de/sitemapproducts0.xml.gz", "https://www.apodiscounter.de/sitemapproducts1.xml.gz"]

    def __init__(self, *args, **kwargs):
        super(ProductUrlSpider, self).__init__(*args, **kwargs)
        self.produkte = set()

        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br, zstd", # 若发现请求回答内容奇怪，试着不用这个请求头
            "Accept-Language": "de-DE,de;q=0.8,en-GB;q=0.5,en;q=0.3",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0"
        }

    def start_requests(self):
        for url in ProductUrlSpider.start_urls:
            yield scrapy.Request(url, headers=self.headers, callback=self.parse, errback=self.errback)

    def errback(self, failure):
        self.logger.error(repr(failure))

    def parse(self, response: HtmlResponse):
        with gzip.GzipFile(fileobj=io.BytesIO(response.body)) as gzip_file:
            xml_content = gzip_file.read()
        xml_str = xml_content.decode()
        response = TextResponse(url='', body=xml_str, encoding='utf-8')
        print(response)

        root = ET.fromstring(response.text)

        namespace = { "ns": "http://www.sitemaps.org/schemas/sitemap/0.9" }
        loc_elements = root.findall(".//ns:loc", namespace)
        loc_values = [loc.text for loc in loc_elements]

        for url in loc_values:
            produkt = url.split('/')[-1]
            if produkt not in self.produkte:
                self.produkte.add(produkt)
                yield {
                    "prod_url": url
                }
