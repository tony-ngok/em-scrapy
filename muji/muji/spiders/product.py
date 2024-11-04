import sys
sys.path.append('..')

from datetime import datetime
from json import loads
from re import findall

import requests
import scrapy
from scrapy.http import HtmlResponse


# scrapy crawl muji_product
class MujiProduct(scrapy.Spider):
    name = "muji_product"
    allowed_domains = ["www.muji.com"]
    start_urls = []

    G_TO_LB = 0.002205
    KG_TO_LB = 2.20462

    custom_settings = {
        "ITEM_PIPELINES": {
            "utils.mongodb.pipelines.pipeline1.MongoPipeLine1": 400,
        }
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
            "Accept-Language": "pt-PT,pt;q=0.8,en-GB;q=0.5,en;q=0.3",
            "Referer": "https://www.google.pt",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0"
        }

        with open('prod_ids.txt', 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    self.start_urls.append(line.strip())
        print(f'Total {len(self.start_urls):_} products'.replace("_", "."))

        self.jpy_rate = 152.327692
        try:
            resp = requests.get('https://open.er-api.com/v6/latest/USD')
            if resp.ok:
                self.jpy_rate = resp.json()['rates']['JPY']
            else:
                raise Exception(f'Status {resp.status_code}')
        except Exception as e:
            print("Fail to get latest USD/JPY rate", str(e))
        finally:
            print(f"USD/JPY rate: {self.jpy_rate:_}".replace(".", ",").replace("_", "."))

    def get_specs(self, txt: str) -> tuple:
        """
        解析商品参数；部分参数（如使用注意事项）加入描述中
        """

        specs = []
        speck_set = set()
        add_descr = []
        weight_str = ""

        # 参数名含有这些字的，要加入表格描述
        to_add_to_descr = ['使用方法', '取扱', '注意', '事項', '成分']

        # 参数名为这些字的，参数值为重复的描述内容（使用方法、使用上注意事项），因而跳过
        speck_to_filter = {'お取扱い上のご注意', 'お取扱い上のご注意２', 'お取扱い上のご注意３', 'お取扱い上のご注意４', 'お取扱い上のご注意５'}

        # 要过滤掉的参数值
        specv_to_filter = {'ー', '取扱説明書に従って正しくお使いください'}

        specs_kmatch = findall(r'{\\\"className\\\":\\\"HeaderCell_cellValue__4rOy0\\\",[^$]*\\\"children\\\":\\\"([^$]*)\\\"}', txt)
        specs_vmatch = findall(r'{\\\"className\\\":\\\"Cell_cellValue__B2F5r\\\",[^$]*\\\"children\\\":\\\"([^$]*)\\\"}', txt)
        if specs_kmatch and specs_vmatch:
            for speck, specv in zip(specs_kmatch, specs_vmatch):
                speck = speck.strip()
                specv = specv.strip()

                if not ((speck in speck_set) or (speck in speck_to_filter) or (specv in specv_to_filter)):
                    speck_set.add(speck)

                    add_to_descr = False
                    for tatd in to_add_to_descr:
                        if tatd in speck:
                            add_descr.append((speck, specv))
                            add_to_descr = True
                            break
                    if not add_to_descr:
                        specs.append({
                            "name": speck,
                            "value": specv
                        })

                        if '重量' in speck:
                            weight_str = specv

        return (specs if specs else None), add_descr, weight_str

    def parse_add_descr(self, add_descr: list) -> str:
        """
        将商品注意事项整理成表，加到描述中
        """

        descr = ""
        for k, v in add_descr:
            descr += f"<tr><th>{k}</th><td>{v}</td></tr>"
        return f'<table class="muji-descr">{descr}</table>' if descr else ""

    def get_weight(self, txt: str) -> float:
        """
        获取商品重量
        """

        weight = None
        w_match = findall(r'(\d*\.?\d+)(kg|g)', txt)
        if w_match:
            if w_match[0][1] == 'kg':
                weight = round(float(w_match[0][0])*self.KG_TO_LB, 2)
            elif w_match[0][1] == 'g':
                weight = round(float(w_match[0][0])*self.G_TO_LB, 2)

        return weight

    def start_requests(self):
        for i, pu in enumerate(self.start_urls, start=1):
            url = 'https://www.muji.com/jp/ja/store/cmdty/detail/'+pu
            print(f"{i:_}".replace('_', '.'), 'https://www.muji.com/jp/ja/store/cmdty/detail/'+pu)
            yield scrapy.Request(url, headers=self.headers, callback=self.parse)

    def parse(self, response: HtmlResponse):
        if response.status == 404:
            print(response.url, "Product not found")
            return

        prod_cont = ""
        prod_specs = ""

        for scr in response.css('script[type="application/ld+json"]::text').getall():
            if '"ProductGroup"' in scr:
                prod_cont = scr
            if prod_cont:
                break

        for scr in response.css('script').getall():
            if 'ProductSpec_productTable__row__A4VGc' in scr:
                prod_specs = scr
            if prod_specs:
                break

        try:
            prod_cont = loads(prod_cont)
            prod_json = prod_cont['hasVariant'][0] # 商品无实际变种
        except:
            print("No product JSON")
            return

        images = ";".join(prod_json.get('image', []))
        if not images:
            print("No images")
            return

        prod_id = prod_json['mpn']

        existence = True
        unavail = {'outofstock', 'soldout'}
        for u in unavail:
            if u in prod_json['offers']['availability'].lower():
                existence = False
                break

        title = prod_json['name']

        descr1 = " ".join(response.css('div.ItemDescriptionChildren_tab__pc__JAWSY > p.ItemDescription_description__e_erj').get("").strip().split())
        descr2 = " ".join(response.css('div.ItemDescriptionChildren_tab__pc__JAWSY > div.ItemDescription_subDescription__YbU_2').get("").strip().split())
        description = f'<div class="muji-descr">{descr1}{descr2}</div>' if descr1 or descr2 else ""

        specifications, add_descr, weight_str = self.get_specs(prod_specs)
        if add_descr:
            description += self.parse_add_descr(add_descr)

        categories = None
        if prod_cont.get('category'):
            cat_list = list(dict.fromkeys(prod_cont['category'].split(" > ")[1:]))
            categories = " > ".join(cat_list)

        price_jpy = float(prod_json['offers']['price'])
        price = round(price_jpy/self.jpy_rate, 2)

        reviews = None
        rating = None
        if prod_json.get('aggregateRating'):
            reviews = prod_json['aggregateRating'].get('reviewCount')
            rating = prod_json['aggregateRating'].get('ratingValue')

        ship_fee = round(500/self.jpy_rate, 2) if price_jpy < 5000 else 0.00
        weight = self.get_weight(weight_str.lower()) if weight_str else None

        yield {
            "date": datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
            "url": response.url,
            "source": "MUJI",
            "product_id": prod_id,
            "existence": existence,
            "title": title,
            "title_en": None,
            "description": description if description else None,
            "description_en": None,
            "summary": None,
            "sku": prod_json['sku'] if prod_json['sku'] else prod_id,
            "upc": prod_json['gtin'],
            "brand": prod_json.get('brand', {}).get('name'),
            "specifications": specifications,
            "categories": categories,
            "images": images,
            "videos": None,
            "price": price,
            "available_qty": 0 if not existence else None,
            "options": None, # 本站商品的所谓变种其实有不同商品URL
            "variants": None,
            "has_only_default_variant": True,
            "returnable": False,
            "reviews": reviews,
            "rating": rating,
            "sold_count": None,
            "shipping_fee": ship_fee,
            "shipping_days_min": 4,
            "shipping_days_max": 8,
            "weight": weight,
            "width": None,
            "length": None,
            "height": None
        }
