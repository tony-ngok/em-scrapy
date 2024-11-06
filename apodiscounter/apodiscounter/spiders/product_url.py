import gzip
import io
import xml.etree.ElementTree as ET

import scrapy
from scrapy.http import HtmlResponse, TextResponse


# scrapy crawl product-url -O
class ProductUrlSpider(scrapy.Spider):
    name = "product-url"
    allowed_domains = ["apodiscounter.de"]
    urls_ausgabe = "apodiscounter_urls.txt"

    # 来源：https://apodiscounter.de/sitemapindex.xml
    start_urls = ["https://www.apodiscounter.de/sitemapproducts0.xml.gz", "https://www.apodiscounter.de/sitemapproducts1.xml.gz"]

    COOKIES = {
        "cf_clearance": "KdF0vW5wk4viGI9MYMXn60_e2E0weSvMYzNXmK88IN0-1730925646-1.2.1.1-3wE2CX2HfHkSHLV2oQgnGhR6LPgQtr1m6p4ac4zlfmFimIfFufcl6CGVxiHTHHz4OXiaM8v818KnolM3bfwrH_MepS6P7mN1_EoYcQp1ECXTuOI3swOje7pA6vDTnGoISlky1GC8451dX.eyFYeCNh2X5zXvdM4vx.ZrK5EY3tiPb5lDAp40g6gz0kBetUHXBqGf9TCsCY6t8Z.Zgm6vpeRjMU7xKL53mvJ3uTZU_a3YZbdfBG9hNBu02V.pAxhHtv69wEmSKZS7TkisULmGmbYSefbMPNNOdV8hZM6Z36JxoQvCm4qegpHMjuFQlkZnv0ax_TO0QSoxNvcKSzDvnK4lK.efA_LBbkLMqKlnrFvWXtzH34h3h58KUzr6yy5liq0BWc4iNR5GvmuYaOZsDhBNWadBhqHAq1ClbPnFGB5Be7pxz1DE_n4A3X1GR0KUx3IMN.uZ6_hY2yIlv3hZSw"
    }

    HEADERS = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
        "Accept-Language": "de-DE,de;q=0.8,en-GB;q=0.5,en;q=0.3",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0"
    }

    def __init__(self, *args, **kwargs):
        super(ProductUrlSpider, self).__init__(*args, **kwargs)
        self.produkte = set()
        self.retry = False

    def start_requests(self):
        for url in ProductUrlSpider.start_urls:
            yield scrapy.Request(url, headers=self.HEADERS, cookies=self.COOKIES, callback=self.parse, errback=self.errback)

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
                self.write_prod(produkt)
                
    def write_prod(self, prod: str):
        mod = 'a' if self.retry else 'w'
        with open(self.urls_ausgabe, mod, encoding='utf-8') as f_urls:
            f_urls.write(prod+'\n')
        if not self.retry:
            self.retry = True
