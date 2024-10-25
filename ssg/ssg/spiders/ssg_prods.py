import json
from datetime import datetime

import requests
import scrapy
from scrapy.http import HtmlResponse


# scrapy crawl ssg_prod
class SsgProds(scrapy.Spider):
    name = "ssg_prod"
    allowed_domains = ["www.ssg.com"]

    custom_settings = {
        'DOWNLOAD_DELAY': 0.1,
        'DOWNLOADER_MIDDLEWARES': { # 每发送请求后，先经过中间件返回回答，然后将回答通过回调函数处理
            'ssg.middlewares.SsgProdsErrsMiddleware': 543
        }
    }

    HEADERS = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "de-DE,de;q=0.9,en-GB;q=0.8,en;q=0.7",
        "connection": "keep-alive",
        "dnt": "1",
        "referer": "",
        "sec-ch-ua": '"Chromium";v="130", "Microsoft Edge";v="130", "Not?A_Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0"
    }

    CM_TO_IN = 0.393701
    G_TO_LB = 0.002205
    KG_TO_LB = 2.20462
    M_TO_IN = 39.37008

    def __init__(self, start_urls: list[str] = [], retry: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = start_urls
        self.retry = retry
        self.output_file = "ssg_products.txt"

        self.krw_rate = 1379.40808
        rate_req = requests.get('https://open.er-api.com/v6/latest/USD')
        if rate_req.ok:
            self.krw_rate = rate_req.json()['rates']['KRW']
            print(f"Latest USD/KRW rate: {self.krw_rate:_}".replace(".", ",").replace("_", "."))
        else:
            print(f"Fail to get latest USD/KRW rate (default: {self.krw_rate:_})".replace(".", ",").replace("_", "."))

    def start_requests(self):
        for i, url in enumerate(self.start_urls):
            url = "https://www.ssg.com/item/itemView.ssg?itemId="+url
            yield scrapy.Request(url, headers=self.HEADERS,
                                 meta={ "cookiejar": i },
                                 callback=self.parse,
                                 cb_kwargs={ "i": i+1 })

    def get_existence(self, stock_txt: str, response: HtmlResponse):
        sold_out = response.css("a.cdtl_btn_soldout")
        return (('instock' in stock_txt) and (not sold_out))

    def get_media(self, img_list: list[str], response: HtmlResponse):
        images = ";".join(["https://"+img for img in img_list])

        vid = response.css('input#vodDataFileNm::attr(value)').get()
        videos = "https://sc3po.ssgcdn.com"+vid+"_h.mp4?w=w" if vid else None

        return (images, videos)
    
    def get_recensions(self, recensions: dict):
        if not recensions:
            return (None, None)
        return (int(recensions["reviewCount"]), round(float(recensions["ratingValue"]), 2))

    def parse(self, response: HtmlResponse, i: int):
        url = response.request.url
        print(f"\n{i:_}/{len(self.start_urls):_}".replace("_", "."), response.request.url)

        now = datetime.now()
        product_id = response.request.url.split("itemId=")[1]

        prod_json = response.css('script[type="application/ld+json"]::text').get()
        if not prod_json:
            print("No product JSON")
            return
        prod_json = json.loads(prod_json)

        images, videos = self.get_media(prod_json.get("image", []))
        if not (images or videos):
            print("No media")
            return

        existence = self.get_existence(prod_json["offers"]["availability"].lower(), response)
        title = prod_json["name"]
        brand = prod_json["brand"]["name"]
        price = round(float(prod_json["offers"]["price"])/self.krw_rate, 2)
        reviews, rating = self.get_recensions(prod_json.get("aggregateRating", {}))

        item = {
            "date": now.strftime('%Y-%m-%dT%H:%M:%S'),
            "url": url,
            "source": "SSG.COM",
            "product_id": product_id,
            "existence": existence,
            "title": title,
            "title_en": None,
            "description_en": None,
            "summary": None,
            "sku": product_id,
            "upc": None,
            "brand": brand,
            "images": images,
            "videos": videos,
            "price": price,
            "returnable": False,
            "reviews": reviews,
            "rating": rating,
            "sold_count": None,
        }
        self.write_item(item)

    def write_item(self, item: dict):
        print(item)

        mode = 'a' if self.retry else 'w'
        with open(self.output_file, mode, encoding='utf-8') as f_out:
            json.dump(item, f_out)
            f_out.write(",\n")
        if not self.retry:
            self.retry = True
