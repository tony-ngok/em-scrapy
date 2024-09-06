from html import unescape
from json import load, loads
import re
from re import findall

from bs4 import BeautifulSoup
from datetime import datetime
import scrapy
from scrapy.http import HtmlResponse


# scrapy crawl aop_product -O aop_products.json
class AopProduct(scrapy.Spider):
    name = "aop_product"
    allowed_domains = ["australianorganicproducts.com.au"]
    start_urls = []

    CM_TO_IN = 0.393701
    G_TO_LB = 0.002205
    M_TO_IN = 39.37008

    # https://australianorganicproducts.com.au/pages/delivery-returns
    SHIP_FEE = 6.63 # 9.95 澳洲元
    FREE_SHIP_PRICE = 85.92 # 129澳洲元以上免费送货

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
            # "Accept-Encoding": "gzip, deflate, br, zstd", # 若发现请求回答内容奇怪，试着不用这个请求头
            "Accept-Language": "es-ES,es;q=0.8,en-GB;q=0.5,en;q=0.3",
            "Cookie": "localization=US; cart_currency=USD",
            "Referer": "https://www.google.es",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0"
        }

        with open('aop_prod_urls.json', 'r') as f:
            produits = load(f)
        self.start_urls = [p['prod_url'] for p in produits]
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

    def get_dims(self, txt: str) -> list:
        """
        获取商品长宽高
        """

        dims = [None, None, None]
        units = [None, None, None]
        dims_out = [None, None, None]

        match1 = findall(r'\b(\d*\.?\d+)\s*([CcMm]*)\s*[Xx]\s*(\d*\.?\d+)\s*([CcMm]*)\s*[Xx]\s*(\d*\.?\d+)\s*([CcMm]+)\b', txt) # 长*宽*高
        match2 = findall(r'\b(\d*\.?\d+)\s*([CcMm]*)\s*[Xx]\s*(\d*\.?\d+)\s*([CcMm]+)\b', txt) # 长*宽
        match3 = findall(r'\b(\d*\.?\d+)\s*([CcMm]+)\b', txt) # 长

        if match1:
            units[2] = match1[0][5].lower()
            units[1] = match1[0][3].lower() if match1[0][3] else units[2]
            units[0] = match1[0][1].lower() if match1[0][1] else units[1]
            for i in range(3):
                dims[i] = float(match1[0][i*2])
        elif match2:
            units[1] = match2[0][3].lower()
            units[0] = match2[0][1].lower() if match2[0][1] else units[1]
            dims[0] = float(match2[0][0])
            dims[1] = float(match2[0][2])
        elif match3:
            units[0] = match3[0][1].lower()
            dims[0] = float(match3[0][0])

        for i, (d, u) in enumerate(zip(dims, units)):
            if u == 'm':
                dims_out[i] = round(d*self.M_TO_IN, 2)
            elif u == 'cm':
                dims_out[i] = round(d*self.CM_TO_IN, 2)

        return dims_out

    def start_requests(self):
        # self.start_urls = [
        #     "https://australianorganicproducts.com.au/collections/gluten-free/products/biotta-organic-beetroot-juice-500ml",
        #     "https://australianorganicproducts.com.au/collections/floss/products/noosa-basics-dental-floss-with-activated-charcoal-bamboo-fibre-35m",
        #     "https://australianorganicproducts.com.au/collections/gift-ideas/products/tisserand-essential-oil-orange-round-9ml",
        #     "https://australianorganicproducts.com.au/collections/organic-natural-chocolate-online/products/vego-whole-hazelnut-chocolate-bar-150g",
        #     "https://australianorganicproducts.com.au/collections/baby-oral-care/products/brauer-baby-child-teething"
        # ] # test

        for i, pu in enumerate(self.start_urls, start=1):
            print(f"{i:_}".replace('_', '.'), pu)
            yield scrapy.Request(pu, headers=self.headers, meta={ 'url': pu }, callback=self.parse)

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
            "sku": var.get('sku', str(var['id'])),
            "option_values": [{
                "name": opt['name'],
                "value": var[f'option{i}']
            } for i, opt in enumerate(options, start=1) if opt != "Title"],
            "images": "https:"+var.get('featured_image', {}).get('src') if var.get('featured_image') else None,
            "price": round(float(var['price'])/100.0, 2),
            "available_qty": var.get('inventory_quantity')
        } for var in var_list if var and var.get('title') != 'Default Title']

        categories = None
        cat_sel = response.css('nav.breadcrumbs-container > a::text')[1:].getall()
        if cat_sel:
            categories = " > ".join([c.strip() for c in cat_sel])

        price = round(float(prod_json['price'])/100.0, 2)

        reviews = None
        rating = None
        r_sel = response.css('div.product-app div.jdgm-prev-badge')
        if r_sel:
            reviews = int(r_sel.css('::attr(data-number-of-reviews)').get())
            rating = round(float(r_sel.css('::attr(data-average-rating)').get()), 1)

        weight = None
        if 'weight' in var_list[0]:
            weight = round(float(var_list[0]['weight'])*self.G_TO_LB, 2)
        
        length, width, height = self.get_dims(title)

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
            "sku": var_list[0].get('sku', str(prod_json['id'])),
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
            "has_only_default_variant": len(variants)<2,
            "returnable": False,
            "reviews": reviews,
            "rating": rating,
            "sold_count": None,
            "shipping_fee": self.SHIP_FEE if price < self.FREE_SHIP_PRICE else 0.00,
            "shipping_days_min": None,
            "shipping_days_max": None,
            "weight": weight,
            "length": length,
            "width": width,
            "height": height,
        }
