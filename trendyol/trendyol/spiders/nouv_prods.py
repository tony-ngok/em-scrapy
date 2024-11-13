# 使用上级目录中的utils
import sys
sys.path.append('..')

from bs4 import BeautifulSoup
import scrapy
from scrapy.http import HtmlResponse


class TrendyolNouvProds(scrapy.Spider):
    name = "trendyol_prod_dat"
    allowed_domains = ['apigw.trendyol.com']
    start_urls = []

    custom_settings = {
        "ITEM_PIPELINES": {
            "trendyol.pipelines.MongoNewsPipeLine": 400,
        }
    }

    def __init__(self, batch: int, referer: str, new_items: list[str] = [], *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.batch = batch
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "fr-FR,fr;q=0.8,en-GB;q=0.5,en;q=0.3",
            "Connection": "keep-alive",
            "Priority": "u=0, i",
            "Referer": referer,
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0"
        }
        self.start_urls = new_items

        print("New items from batch", batch+1)

    def start_requests(self):
        for i, dat in enumerate(self.start_urls):
            item = dat['item']
            video_id = dat['video_id']

            if dat['has_more_descr']:
                pid = item['product_id']
                req_url2 = f"https://apigw.trendyol.com/discovery-web-productgw-service/api/product-detail/{pid}/html-content?channelId=1"
                yield scrapy.Request(req_url2, headers=self.headers,
                                     meta={ "cookiejar": i },
                                     callback=self.parse_descr_page,
                                     cb_kwargs={ "item": item, "video_id": video_id })
            elif video_id:
                req_url3 = f'https://apigw.trendyol.com/discovery-web-websfxmediacenter-santral/video-content-by-id/{video_id}?channelId=1'
                yield scrapy.Request(req_url3, headers=self.headers,
                                    meta={ "cookiejar": i },
                                    callback=self.parse_video,
                                    cb_kwargs={ "item": item })
            else:
                yield item

    def parse_descr_page(self, response: HtmlResponse, item: dict, video_id: str):
        i = response.meta['cookiejar']
        if response.status in range(200, 300):
            descr_info = item['description']

            descr_page = response.json()['result']
            descr_page = '' if not descr_page else " ".join(descr_page.replace('id="rich-content-wrapper"', 'class="trendyol-descr"').strip().split())

            description = descr_info+descr_page
            item['description'] = description if description else None
        else:
            item['description'] = item['description'] if item['description'] else None

        if video_id:
            req_url3 = f'https://apigw.trendyol.com/discovery-web-websfxmediacenter-santral/video-content-by-id/{video_id}?channelId=1'
            yield scrapy.Request(req_url3, headers=self.headers,
                                  meta={ "cookiejar": i },
                                  callback=self.parse_video,
                                  cb_kwargs={ "item": item })
        else:
            yield item

    def parse_video(self, response: HtmlResponse, item: dict):
        if response.status in range(200, 300):
            item['videos'] = response.json().get('result', {}).get('url')
        yield item
