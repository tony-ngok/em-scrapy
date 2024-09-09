from html import unescape
from json import load, loads
import re
from re import findall

from datetime import datetime
import scrapy
from scrapy.http import HtmlResponse


# scrapy crawl muji_product -o muji_products.json # 增添数据（不复写）
# scrapy crawl muji_product -O muji_products.json # 复写整个数据
class MujiProduct(scrapy.Spider):
    name = "muji_product"
    allowed_domains = ["www.muji.com"]
    start_urls = []

    JPY_TO_USD = 1.0/142.71
    FREE_SHIP_PRICE = 5000*JPY_TO_USD
    SHIP_FEE = 500*JPY_TO_USD

    CM_TO_IN = 0.393701
    M_TO_IN = 39.37008
    G_TO_LB = 0.002205
    KG_TO_LB = 2.20462

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
            # "Accept-Encoding": "gzip, deflate, br, zstd", # 若发现请求回答内容奇怪，试着不用这个请求头
            "Accept-Language": "pt-PT,pt;q=0.8,en-GB;q=0.5,en;q=0.3",
            "Referer": "https://www.google.pt",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0"
        }

        with open('muji_prod_urls.json', 'r') as f:
            produits = load(f)
        self.start_urls = [p['prod_url'] for p in produits]
        print(f'Total {len(self.start_urls):_} products'.replace("_", "."))
    
    def get_specs(self, txt: str) -> tuple:
        """
        解析商品参数；部分参数（如使用注意事项）加入描述中
        """

        specs = []


        specs_match = (r'')

    def get_dims(self, txt: str) -> list:
        """
        获取商品长宽高
        """

        dims = [None, None, None]
        units = [None, None, None]
        dims_out = [None, None, None]

        match1 = findall(r'\b[w]*(\d*\.?\d+)\s*([cm]*)\s*[x|×]\s*[h]*(\d*\.?\d+)\s*([cm]*)\s*[x|×]\s*[d|l]*(\d*\.?\d+)\s*([cm]+)\b', txt) # 宽*高*长
        match2 = findall(r'\b[w]*(\d*\.?\d+)\s*([cm]*)\s*[x|×]\s*[d|l]*(\d*\.?\d+)\s*([cm]+)\b', txt) # 宽*长
        match3 = findall(r'\b[d|l]*(\d*\.?\d+)\s*([cm]+)\b', txt) # 长

        if match1:
            units[2] = match1[0][5]
            units[1] = match1[0][3] if match1[0][3] else units[2]
            units[0] = match1[0][1] if match1[0][1] else units[1]
            for i in range(3):
                dims[i] = float(match1[0][i*2])
        elif match2:
            units[2] = match2[0][3]
            units[0] = match2[0][1] if match2[0][1] else units[1]
            dims[0] = float(match2[0][0])
            dims[2] = float(match2[0][2])
        elif match3:
            units[2] = match3[0][1]
            dims[2] = float(match3[0][0])

        for i, (d, u) in enumerate(zip(dims, units)):
            if u == 'm':
                dims_out[i] = round(d*self.M_TO_IN, 2)
            elif u == 'cm':
                dims_out[i] = round(d*self.CM_TO_IN, 2)

        return dims_out

    def start_requests(self):
        self.start_urls = [
            "https://www.muji.com/jp/ja/store/cmdty/detail/4550583467395",
            "https://www.muji.com/jp/ja/store/cmdty/detail/4550583484514",
            "https://www.muji.com/jp/ja/store/cmdty/detail/4550344295236"
        ] # test

        for i, pu in enumerate(self.start_urls, start=1):
            print(f"{i:_}".replace('_', '.'), pu)
            yield scrapy.Request(pu, headers=self.headers, meta={ 'url': pu }, callback=self.parse)

    def parse(self, response: HtmlResponse):
        prod_cont = ""
        prod_specs = ""
        
        for scr in response.css('script[type="application/ld+json"]::text').getall():
            if '"ProductGroup"' in scr:
                prod_cont = scr
            if prod_cont:
                break
        
        for scr in response.css('script'):
            if 'ProductSpec_productTable__row__A4VGc' in scr:
                prod_specs = scr
            if prod_specs:
                break
        
        try:
            prod_cont = loads(prod_cont)
            prod_json = prod_cont['hasVariant'][0] # 商品无实际变种
        except:
            return

        images = ";".join(prod_json.get('image', []))
        if not images:
            return

        prod_id = prod_json['mpn']
        existence = 'instock' in prod_json['offers']['availability'].lower()
        title = prod_json['name']

        descr1 = response.css('div.ItemDescriptionChildren_tab__pc__JAWSY > p.ItemDescription_description__e_erj').get().replace('\n', ' ').replace('\r', ' ')
        descr2 = response.css('div.ItemDescriptionChildren_tab__pc__JAWSY > div.ItemDescription_subDescription__YbU_2').get().replace('\n', ' ').replace('\r', ' ')
        description = f'<div class="muji-descr">{descr1}{descr2}</div>'
        # print(description+'\n') 

        specifications, more_descr = self.get_specs(prod_specs)

        categories = None
        if prod_cont.get('category'):
            cat_list = list(dict.fromkeys(prod_cont['category'].split(" > ")[1:]))
            categories = " > ".join(cat_list)
        
        price = round(float(prod_json['offers']['price'])*self.JPY_TO_USD, 2)

        reviews = None
        rating = None
        if prod_json.get('aggregateRating'):
            reviews = prod_json['aggregateRating'].get('reviewCount')
            rating = prod_json['aggregateRating'].get('ratingValue')

        weight = None
        # if 'weight' in var_list[0]:
        #     weight = round(float(var_list[0]['weight'])*self.G_TO_LB, 2)
        
        width, height, length = self.get_dims(title.lower())

        yield {
            "date": datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
            "url": response.meta['url'],
            "source": "MUJI",
            "product_id": prod_id,
            "existence": existence,
            "title": title,
            "title_en": None,
            "description": description,
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
            "shipping_fee": round((self.SHIP_FEE if price < self.FREE_SHIP_PRICE else 0.00), 2),
            "shipping_days_min": 4,
            "shipping_days_max": 8,
            "weight": weight,
            "width": width,
            "height": height,
            "length": length,
        }
