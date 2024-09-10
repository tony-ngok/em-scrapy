import gzip
import io
import xml.etree.ElementTree as ET
from datetime import datetime
# from urllib.parse import urlparse, urlunparse

import scrapy
# from apodiscounter.items import ProductUrlItem

# from resources.base_spider import BaseSpider


# scrapy crawl product-url -O apodiscounter_produkturls.json
class ProductUrlSpider(scrapy.Spider):
    name = "product-url"
    allowed_domains = ["shop-apodiscounter.com"]

    # 来源：https://apodiscounter.de/sitemapindex.xml
    start_urls = ["https://www.apodiscounter.de/sitemapproducts0.xml.gz", "https://www.apodiscounter.de/sitemapproducts1.xml.gz"]

    # custom_settings = {
    #     "ITEM_PIPELINES": {
    #         "apodiscounter.pipelines.ProductUrlPipeline": 400,
    #     }
    # }

    def __init__(self, *args, **kwargs):
        super(ProductUrlSpider, self).__init__(*args, **kwargs)
        # self.cookies = {
        #     "__cq_dnt": "1",
        #     "dw_dnt": "1",
        #     "cc-nx-g_Global": "9GZDwp_F_6D27Bc-Gef3dfTjyaZp6Df4bWikeRswIoA",
        #     "dwanonymous_f05b8449cdeb698aa739d69c70fdf52a": "abkVEmmlnYm4TSBywTaARyP8V5",
        #     "_gcl_au": "1.1.779525251.1724183068",
        #     "_ga": "GA1.1.169330906.1724183068",
        #     "_scid": "ba7c43a3-15f9-435f-a2c8-a023c1a61f46",
        #     "_pin_unauth": "dWlkPU1ESTVPV00yTmpNdFpESXpZaTAwT0RrNUxXSTVaREF0WkRFMU1ERXlNVEl4TW1VeA",
        #     "FPID": "FPID2.2.ScT2LL8wdvHtS6s1sfK%2BR9fNaXVu4ViI0XFa5MmvCuk%3D.1724183068",
        #     "FPLC": "bQHOccDYLEpsFIMcf77UwKFEeNFDS1LrrEN5WQL%2BTr%2FlemDJHh2suWZf6fqfX6BVXO3bWtlJ1IaUqdFj40an4UOl2Y0fDDRXMcQ0nj%2Bt6YI2pl%2F2VFfJp%2B%2B5iW5Dzw%3D%3D",
        #     "_hjSessionUser_467620": "eyJpZCI6IjY5Nzk1MzU1LTcwOWItNWZlYi1iMDdlLTMxMTcwMTQ4YmY0NyIsImNyZWF0ZWQiOjE3MjQxODMwNzMyMDUsImV4aXN0aW5nIjp0cnVlfQ==",
        #     "_ScCbts": "%5B%5D",
        #     "OptanonAlertBoxClosed": "2024-08-20T19:44:35.096Z",
        #     "_apodiscounterLocale": "US|US|en_US",
        #     "source": "aw",
        #     "dwanonymous_7254072e2668c23dc3bf6cca213a6657": "belck3lHaUmesRlXoVmbYYlXE0",
        #     "dwsecuretoken_7254072e2668c23dc3bf6cca213a6657": '""',
        #     "cc-nx-g_US": "1rQgqulO4hWgtsFmufhXuf6m3HkOs87w7DHKVEODkr0",
        #     "_hjSession_467620": "eyJpZCI6ImJlYmM5ZTAzLWQ5Y2YtNDc1ZC1iMmViLWZlM2YzMDljNjJkNCIsImMiOjE3MjQyNDUxODA2MjgsInMiOjEsInIiOjEsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjowLCJzcCI6MH0=",
        #     "dwsid": "rGm1-VCl7Hr7eb_u9m0HocyXpea5gDNpbI3_s3NUowD3qr1wqtJ7p4JEU0nZ9__4QGHPA5WKWZK63rgKqlJBWg==",
        #     "sid": "0TvNWq7oBGdFpjOBQNJXeLHF3UVHzdt00lI",
        #     "lantern": "63a31df7-e15a-4536-b6d5-a28b44d80c69",
        #     "_scid_r": "ba7c43a3-15f9-435f-a2c8-a023c1a61f46",
        #     "_ga_8EBNFBYE4T": "GS1.1.1724245180.3.1.1724247381.0.0.244902555",
        #     "OptanonConsent": "isGpcEnabled=0&datestamp=Wed+Aug+21+2024+08%3A36%3A22+GMT-0500+(Central+Daylight+Time)&version=202402.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=7e0040ba-9d84-4090-9266-e6612662d837&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0003%3A1%2CC0001%3A1%2CC0004%3A1%2CC0007%3A1%2CBG28%3A1&geolocation=US%3BMO&AwaitingReconsent=false",
        #     "_uetsid": "a3b0de505f2c11efa0a3bf2d7263a5e9|1i66y5t|2|foi|0|1693",
        #     "_ga_KF76XGL9WS": "GS1.1.1724245181.2.1.1724247383.13.0.0",
        #     "_uetvid": "a3b0ff805f2c11ef8fc05d00fc81dc28|cuijyy|1724247383816|6|1|bat.bing.com/p/insights/c/l",
        # }

        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br, zstd", # 若发现请求回答内容奇怪，试着不用这个请求头
            "Accept-Language": "de-DE,de;q=0.8,en-GB;q=0.5,en;q=0.3",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0"
        }

    def start_requests(self):
        for url in ProductUrlSpider.start_urls:
            if "products" not in url:
                continue
            yield scrapy.Request(
                url,
                # method="GET",
                # headers=self.get_headers(),
                # cookies=self.cookies,
                callback=self.parse,
                errback=self.errback
            )

    # def get_headers(self):
    #     return {
    #         "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    #         "accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
    #         "cache-control": "no-cache",
    #         "pragma": "no-cache",
    #         "priority": "u=0, i",
    #         "referer": "http://35.192.187.156/",
    #         "sec-ch-ua": '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
    #         "sec-ch-ua-mobile": "?0",
    #         "sec-ch-ua-platform": '"Linux"',
    #         "sec-fetch-dest": "document",
    #         "sec-fetch-mode": "navigate",
    #         "sec-fetch-site": "cross-site",
    #         "sec-fetch-user": "?1",
    #         "upgrade-insecure-requests": "1",
    #         "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    #     }

    def errback(self, failure):
        self.logger.error(repr(failure))

    # def get_product_id(self, url):
    #     parse_usl = urlparse(url)
    #     return parse_usl.path

    def parse(self, response):
        root = ET.fromstring(response.text)

        namespace = { "ns": "http://www.sitemaps.org/schemas/sitemap/0.9" }
        loc_elements = root.findall(".//ns:loc", namespace)
        loc_values = [loc.text for loc in loc_elements]

        for url in loc_values:
            # if "products" in url:
            #     continue
            # item = ProductUrlItem()
            # item["id"] = self.get_product_id(url)
            # item["url"] = url
            # item["date"] = datetime.now().replace(microsecond=0).isoformat()
            # yield item

            yield {
                "prod_url": url
            }
