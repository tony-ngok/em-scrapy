from datetime import datetime
from json import loads

import requests
from bs4 import BeautifulSoup, Tag
import scrapy
from scrapy.http import HtmlResponse


# scrapy crawl aop_product
class AopProduct(scrapy.Spider):
    name = "aop_product"
    allowed_domains = ["australianorganicproducts.com.au"]
    start_urls = []

    G_TO_LB = 0.002205

    custom_settings = {
        "ITEM_PIPELINES": {
            "utils.mongodb.pipelines.pipeline1.MongoPipeLine1": 400,
        }
    }

    HEADERS = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.8,en-GB;q=0.5,en;q=0.3",
        "Referer": "https://www.google.es",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0"
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        with open('aop_prod_urls.txt', 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    self.start_urls.append(line.strip())
        print(f'Total {len(self.start_urls):_} products'.replace("_", "."))

        self.aud_rate = 1.507897
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

    def get_description(self, soup) -> str:
        descr = ""

        for child in soup.children:
            if isinstance(child, str) and child.strip():
                if ('Why buy from us?' in child) or (child.strip().endswith('on sale!')):
                    descr += "DESCR_END"
                descr += " ".join(child.strip().split())
            elif isinstance(child, Tag) and (child.name != 'a'):
                in_txt = self.get_description(child)
                if 'DESCR_END' in in_txt:
                    break
                elif in_txt:
                    descr += f'<{child.name}>{in_txt}</{child.name}>'

        return descr

    def start_requests(self):
        for i, pu in enumerate(self.start_urls, start=1):
            cat, name = pu.split()
            url = f"https://australianorganicproducts.com.au/collections/{cat}/products/{name}"
            print(f"{i:_}".replace('_', '.'), url)
            yield scrapy.Request(url, headers=self.HEADERS, callback=self.parse)

    def parse(self, response: HtmlResponse):
        if response.status == 404:
            print("Product not found", response.url)
            return

        try:
            prod_scr = response.css('script[data-section-type="static-product"]::text').get()
            prod_json = loads(prod_scr)['product']
        except:
            print("Fail to get product JSON")
            return

        images = ";".join('https:'+img.split('?')[0] for img in prod_json.get('images', []))
        if not images:
            print("No images")
            return

        existence = prod_json['available']
        title = prod_json['title']

        descr_txt = response.css('div.product-description > *').get('')
        description = self.get_description(BeautifulSoup(descr_txt, 'html.parser')) if descr_txt else None
        if description:
            description = f'<div class="aop-descr">{description}</div>'

        options = [{
            "id": None,
            "name": opt
        } for opt in prod_json.get('options', []) if opt != "Title"]    

        var_list = [var for var in prod_json.get('variants', [{}])]
        variants = [{
            "variant_id": str(var['id']),
            "barcode": var.get('barcode') or None,
            "sku": var.get('sku') if var.get('sku') else str(var['id']),
            "option_values": [{
                "option_id": None,
                "option_value_id": None,
                "option_name": opt['name'],
                "option_value": var[f'option{i}']
            } for i, opt in enumerate(options, start=1) if opt != "Title"],
            "images": "https:"+var.get('featured_image', {})['src'].split('?')[0] if var.get('featured_image') else None,
            "price": round(float(var['price'])/100.0, 2),
            "available_qty": var.get('inventory_quantity')
        } for var in var_list if var] if options else None

        categories = None
        cat_sel = response.css('nav.breadcrumbs-container > a::text')[1:].getall()
        if cat_sel:
            categories = " > ".join([c.strip() for c in cat_sel])

        price_aud = float(prod_json['price'])/100.0
        price = round(price_aud*self.aud_rate, 2)

        reviews = None
        rating = None
        r_sel = response.css('div.product-app div.jdgm-prev-badge')
        if r_sel:
            reviews = int(r_sel.css('::attr(data-number-of-reviews)').get())
            rating = round(float(r_sel.css('::attr(data-average-rating)').get()), 1)

        weight = None
        if 'weight' in var_list[0]:
            weight = round(float(var_list[0]['weight'])*0.002205, 2)

        yield {
            "date": datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
            "url": response.url,
            "source": "Australian Organic Products",
            "product_id": str(prod_json['id']),
            "existence": existence,
            "title": title,
            "title_en": title,
            "description": description,
            "description_en": None,
            "summary": None,
            "sku": var_list[0].get('sku') if var_list[0].get('sku') else str(prod_json['id']),
            "upc": var_list[0].get('barcode'),
            "brand": prod_json.get('vendor'),
            "specifications": None,
            "categories": categories,
            "images": images,
            "videos": None,
            "price": price,
            "available_qty": var_list[0].get('inventory_quantity', (0 if not existence else None)),
            "options": options if options else None,
            "variants": variants if variants else None,
            "has_only_default_variant": (len(variants) < 2) if variants else True,
            "returnable": False,
            "reviews": reviews,
            "rating": rating,
            "sold_count": None,
            "shipping_fee": round(9.95*self.aud_rate, 2) if price_aud < 129.00 else 0.00, # https://australianorganicproducts.com.au/pages/delivery-returns
            "shipping_days_min": None,
            "shipping_days_max": None,
            "weight": weight,
            "length": None,
            "width": None,
            "height": None,
        }
