from html import unescape
from json import loads
import re

from datetime import datetime
import scrapy
from scrapy.http import HtmlResponse


# scrapy crawl aop_product
class AopProduct(scrapy.Spider):
    name = "aop_product"
    allowed_domains = ["australianorganicproducts.com.au"]
    start_urls = []

    AUD_TO_USD = 0.6670
    CM_TO_IN = 0.393701
    G_TO_LB = 0.002205
    M_TO_IN = 39.37008

    # https://australianorganicproducts.com.au/pages/delivery-returns
    SHIP_FEE = 9.95*AUD_TO_USD
    FREE_SHIP_PRICE = 129.00*AUD_TO_USD

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
    
    def get_description(self, txt: str) -> str:
        """
        解析格式为“标题+内容+标题+内容...”的商品描述，并过滤掉促销资讯
        """

        if txt:
            txt = unescape(txt).replace('\n', ' ').replace('\r', ' ')
            txt = ''.join([s.strip() for s in re.split(r'(?=<h[2-4][^>]*>)', txt) if s.strip()
                            and 'Why buy from us?' not in s
                            and 'discounted price' not in s
                            and 'Click here' not in s
                            and 'Range here' not in s])
        
        return f'<div class="aop-descr">{txt}</div>'

    def start_requests(self):
        for i, pu in enumerate(self.start_urls, start=1):
            print(f"{i:_}".replace('_', '.'), pu)
            yield scrapy.Request(pu, headers=self.HEADERS, meta={ 'url': pu }, callback=self.parse)

    def parse(self, response: HtmlResponse):
        try:
            prod_scr = response.css('script[data-section-type="static-product"]::text').get()
            prod_json = loads(prod_scr)['product']
        except:
            return

        images = ";".join('https:'+img for img in prod_json.get('images', []))
        if not images:
            return

        existence = prod_json['available']
        title = prod_json['title']

        description = self.get_description(prod_json.get('description', ''))
        # print(description+'\n') 

        options = [{
            "id": None,
            "name": opt
        } for opt in prod_json.get('options', []) if opt != "Title"]    
        
        var_list = [var for var in prod_json.get('variants', [{}])]
        variants = [{
            "variant_id": str(var['id']),
            "barcode": var.get('barcode'),
            "sku": var.get('sku') if var.get('sku') else str(var['id']),
            "option_values": [{
                "option_id": None,
                "option_value_id": None,
                "option_name": opt['name'],
                "option_value": var[f'option{i}']
            } for i, opt in enumerate(options, start=1) if opt != "Title"],
            "images": "https:"+var.get('featured_image', {}).get('src') if var.get('featured_image') else None,
            "price": round(float(var['price'])/100.0, 2),
            "available_qty": var.get('inventory_quantity')
        } for var in var_list if var] if options else None

        categories = None
        cat_sel = response.css('nav.breadcrumbs-container > a::text')[1:].getall()
        if cat_sel:
            categories = " > ".join([c.strip() for c in cat_sel])

        price = round(float(prod_json['price'])/100.0*self.AUD_TO_USD, 2)

        reviews = None
        rating = None
        r_sel = response.css('div.product-app div.jdgm-prev-badge')
        if r_sel:
            reviews = int(r_sel.css('::attr(data-number-of-reviews)').get())
            rating = round(float(r_sel.css('::attr(data-average-rating)').get()), 1)

        weight = None
        if 'weight' in var_list[0]:
            weight = round(float(var_list[0]['weight'])*self.G_TO_LB, 2)

        yield {
            "date": datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
            "url": response.meta['url'],
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
            "has_only_default_variant": len(variants)<2 if variants else True,
            "returnable": False,
            "reviews": reviews,
            "rating": rating,
            "sold_count": None,
            "shipping_fee": round((self.SHIP_FEE if price < self.FREE_SHIP_PRICE else 0.00), 2),
            "shipping_days_min": None,
            "shipping_days_max": None,
            "weight": weight,
            "length": None,
            "width": None,
            "height": None,
        }
