# 使用上级目录中的utils
import sys
sys.path.append('..')

from datetime import datetime
from html import unescape
from json import loads

import requests
from bs4 import BeautifulSoup, Tag
import scrapy
from scrapy.http import HtmlResponse


# scrapy crawl po_product
class POProductSpider(scrapy.Spider):
    """
    商品明细页大部分内容为传统HTML，因此可直接用Scrapy抓取
    """

    name = "po_product"
    allowed_domains = ['www.pharmacyonline.com.au']
    start_urls = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
            "Accept-Language": "es-ES,es;q=0.8,en-GB;q=0.5,en;q=0.3",
            "Referer": "https://www.google.es",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0"
        }

        with open('po_prod_links.txt', 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    self.start_urls.append(line.strip())
        print(f'Total {len(self.start_urls):_} unique products'.replace("_", "."))

        self.aud_rate = 1.517678
        try:
            resp = requests.get('https://open.er-api.com/v6/latest/USD')
            if resp.ok:
                self.aud_rate = resp.json()['rates']['AUD']
            else:
                raise Exception(f'Status {resp.status_code}')
        except Exception as e:
            print("Fail to get latest USD/AUD rate", str(e))
        finally:
            print(f"USD/AUD rate: {self.aud_rate:_}".replace(".", ",").replace("_", "."))

    def start_requests(self):
        for i, todo in enumerate(self.start_urls):
            todo_split = todo.split("|")
            url = 'https://www.pharmacyonline.com.au/'+todo_split[0]
            cats = todo_split[1]

            if len(todo_split) >= 3:
                weight_g = float(todo_split[2])
            else:
                weight_g = 0.0

            yield scrapy.Request(url, headers=self.headers, callback=self.parse,
                                 cb_kwargs={ "cats": cats, "weight_g": weight_g })

    def parse_descr(self, soup):
        descr = ""

        for child in soup.children:
            if isinstance(child, str):
                descr += " ".join(child.strip().split())
            elif isinstance(child, Tag) and (child.name not in {'a', 'script'}) and ('product-promotion-text' not in child.get('class', [])):
                sub_descr = self.parse_descr(child)
                if sub_descr:
                    descr += f'<{child.name}>{sub_descr}</{child.name}>'

        return descr

    def get_all_descr(self, response: HtmlResponse):
        all_descr = ""

        feat_sel = response.css('div.description').get('')
        if feat_sel:
            all_descr += "<h1>Product Description & Features</h1>"
            all_descr += self.parse_descr(BeautifulSoup(feat_sel, 'html.parser'))
        
        dir_sel = response.css('div#directions_for_use').get('')
        if dir_sel:
            all_descr += "<h1>Directions For Use</h1>"
            all_descr += self.parse_descr(BeautifulSoup(dir_sel, 'html.parser'))
        
        ingr_sel = response.css('div#ingredients_material').get('')
        if ingr_sel:
            all_descr += "<h1>Ingredients/Material</h1>"
            all_descr += self.parse_descr(BeautifulSoup(ingr_sel, 'html.parser'))
        
        warn_sel = response.css('div#product_info_warnings').get('')
        if warn_sel:
            all_descr += "<h1>Warnings and Disclaimers</h1>"
            all_descr += self.parse_descr(BeautifulSoup(warn_sel, 'html.parser'))
        
        return all_descr if all_descr else None

    def get_media(self, response: HtmlResponse):
        images = []
        videos = []

        media_list = None
        for scr in response.css('script[type="text/x-magento-init"]::text').getall():
            if 'mage/gallery/gallery' in scr:
                media_list = loads(scr)['[data-gallery-role=gallery-placeholder]']['mage/gallery/gallery'].get('data', [])
            if media_list:
                for med in media_list:
                    if (med['type'] == 'image') and ('thumb_prescription_pharmacy' not in med['full']):
                        images.append(med['full'].split('?')[0])
                    elif (med['type'] == 'video') and med['videoUrl']:
                        videos.append(med['videoUrl'])

                images = ";".join(images)
                videos = ";".join(videos)
                break

        return images, videos

    def parse(self, response: HtmlResponse, cats: str, weight_g: float = 0.0):
        """
        从下载下来的HTML中解析数据字段\n
        注意事项：
        1. 没有图的商品卖不出去，只能扔掉
        2. 配送资料统一以国内邮寄为准（不考虑国际邮寄）
        """

        # 没有图的商品卖不出去，只能扔掉
        images, videos = self.get_media(response)
        if not (images or videos):
            print("No media")
            return
        if not videos:
            videos = None

        prod_id = response.css('div[itemprop="sku"]::text').get().strip()
        
        existence = True
        exist_resp = response.css('span.status')
        if not (exist_resp and (exist_resp.css('::text').get('').strip().lower() == 'in stock')):
            existence = False

        title = unescape(response.css('span.base::text').get().strip())
        description = self.get_all_descr(response)

        upc = None
        upc_sel = response.css('meta[itemprop="gtin14"]::attr(content)')
        if upc_sel:
            upc = upc_sel.get().strip()
       
        brand = None
        brand_sel = response.css('div.brand::attr(data-brand)')
        if brand_sel:
            brand = brand_sel.get().strip()

        categories = " > ".join(cats.split(";"))

        price_aud = float(response.css('meta[property="product:price:amount"]::attr(content)').get().strip())
        price = round(price_aud/self.aud_rate, 2)

        reviews = 0
        review_sel = response.css('div#bvseo-aggregateRatingSection > span.bvseo-reviewCount::text')
        if review_sel:
            reviews = int(review_sel.get().strip())
        
        rating = 0.0
        rating_sel = response.css('div#bvseo-aggregateRatingSection > span.bvseo-ratingValue::text')
        if rating_sel:
            rating = round(float(rating_sel.get().strip()), 1)

        weight = round(weight_g*0.002205, 2) if weight_g else None

        yield {
            "date": datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
            "url": response.url,
            "source": "Pharmacy Online",
            "product_id": prod_id,
            "existence": existence,
            "title": title,
            "title_en": title,
            "description": description,
            "description_en": None,
            "summary": None,
            "sku": prod_id,
            "upc": upc,
            "brand": brand,
            "specifications": None,
            "categories": categories,
            "images": images,
            "videos": videos,
            "price": price,
            "available_qty": 0 if not existence else None,
            "options": None,
            "variants": None,
            "has_only_default_variant": True,
            "returnable": False,
            "reviews": reviews,
            "rating": rating,
            "sold_count": None,
            "shipping_fee": round(9.95/self.aud_rate, 2) if price_aud < 125.00 else 0.00, # https://www.pharmacyonline.com.au/delivery
            "shipping_days_min": None,
            "shipping_days_max": None,
            "weight": weight,
            "length": None,
            "width": None,
            "height": None
        }
