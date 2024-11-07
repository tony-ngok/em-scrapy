# 使用上级目录中的utils
import sys
sys.path.append('..')

from html import unescape
from json import load, loads
import re
from re import findall

from datetime import datetime
import scrapy
from scrapy.http import HtmlResponse


# scrapy crawl monotaro_product -o monotaro_products.json # 增添数据（不复写）
# scrapy crawl monotaro_product -O monotaro_products.json # 复写整个数据
class MonotaroProduct(scrapy.Spider):
    name = "monotaro_product"
    allowed_domains = ["www.monotaro.com"]
    start_urls = []

    JPY_TO_USD = 1.0/143.13

    # https://help.monotaro.com/app/answers/detail/a_id/19
    FREE_SHIP_PRICE = 3500*JPY_TO_USD
    SHIP_FEE = 500*JPY_TO_USD

    CM_TO_IN = 0.393701
    M_TO_IN = 39.37008
    MM_TO_IN = 0.0393701
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

        with open('monotaro_prod_urls.json', 'r') as f:
            produits = load(f)
        self.start_urls = [p['prod_url'] for p in produits]
        print(f'Total {len(self.start_urls):_} products'.replace("_", "."))
    
    def get_id(self, url: str) -> str:
        """
        从商品URL中提取商品号
        """

        id_match = findall(r'/g/(\d+)', url)
        if id_match:
            return id_match[0]

    def get_specs(self, txt: str) -> tuple:
        """
        解析商品参数；部分参数（如使用注意事项）加入描述中
        """

        # TODO
        specs = []
        speck_set = set()
        add_descr = []
        weight_str = ""
        dims_str = ""

        specs_kmatch = findall(r'{\\\"className\\\":\\\"HeaderCell_cellValue__4rOy0\\\",[^$]*\\\"children\\\":\\\"([^$]*)\\\"}', txt)
        specs_vmatch = findall(r'{\\\"className\\\":\\\"Cell_cellValue__B2F5r\\\",[^$]*\\\"children\\\":\\\"([^$]*)\\\"}', txt)
        # print(specs_vmatch)
        if specs_kmatch and specs_vmatch:
            for speck, specv in zip(specs_kmatch, specs_vmatch):
                speck = speck.replace(' ', '')
                if speck not in speck_set:
                    speck_set.add(speck)

                    if ('使用' in speck) or ('取扱' in speck):
                        add_descr.append((speck, specv))
                    else:
                        specs.append({
                            "name": speck,
                            "value": specv
                        })

                        if '外寸' in speck:
                            dims_str = specv
                        if '重量' in speck:
                            weight_str = specv
        
        return ((specs if specs else None), add_descr, weight_str, dims_str)

    def parse_add_descr(self, add_descr: list) -> str:
        """
        将商品注意事项整理成表，加到描述中
        """

        descr = '<table class="monotaro-descr">'
        for k, v in add_descr:
            descr += f"<tr><th>{k}</th><td>{v}</td></tr>"
        descr += '</table>'
        return descr

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

    def get_dims(self, txt: str) -> list:
        """
        获取商品长宽高
        """

        dims = [None, None, None]
        units = [None, None, None]
        dims_out = [None, None, None]

        match1 = findall(r'[w]*(\d*\.?\d+)\s*([cm]*)\s*[x|×]\s*[d|l]*(\d*\.?\d+)\s*([cm]*)\s*[x|×]\s*[h]*(\d*\.?\d+)\s*([cm]+)', txt) # 宽*长*高
        match2 = findall(r'[w]*(\d*\.?\d+)\s*([cm]*)\s*[x|×]\s*[d|l]*(\d*\.?\d+)\s*([cm]+)', txt) # 宽*长
        match3 = findall(r'[d|l]*(\d*\.?\d+)\s*([cm]+)', txt) # 长

        if match1:
            units[2] = match1[0][5]
            units[1] = match1[0][3] if match1[0][3] else units[2]
            units[0] = match1[0][1] if match1[0][1] else units[1]
            for i in range(3):
                dims[i] = float(match1[0][i*2])
        elif match2:
            units[1] = match2[0][3]
            units[0] = match2[0][1] if match2[0][1] else units[1]
            dims[0] = float(match2[0][0])
            dims[1] = float(match2[0][2])
        elif match3:
            units[1] = match3[0][1]
            dims[1] = float(match3[0][0])

        for i, (d, u) in enumerate(zip(dims, units)):
            if u == 'm':
                dims_out[i] = round(d*self.M_TO_IN, 2)
            elif u == 'cm':
                dims_out[i] = round(d*self.CM_TO_IN, 2)

        return dims_out

    def start_requests(self):
        # self.start_urls = [
        #     "https://www.monotaro.com/g/04191960/",
        #     "https://www.monotaro.com/g/00317720/",
        #     "https://www.monotaro.com/g/04563190/"
        # ] # test

        for i, pu in enumerate(self.start_urls, start=1):
            print(f"{i:_}".replace('_', '.'), pu)
            yield scrapy.Request(pu, headers=self.headers, meta={ 'url': pu }, callback=self.parse)

    def parse(self, response: HtmlResponse):
        prod_json = ""
        bc_json = ""
        
        for scr in response.css('script[type="application/ld+json"]::text').getall():
            if '"Product"' in scr:
                prod_json = scr
            elif 'BreadCrumbList"' in scr:
                bc_json = scr
            if prod_json and bc_json:
                break
        
        try:
            prod_json = loads(prod_json)
            bc_json = loads(bc_json)
        except:
            return

        images = ";".join(prod_json.get('image', []))
        if not images:
            return

        url = response.meta['url']
        prod_id = self.get_id(url)
        existence = 'instock' in prod_json['offers']['availability'].lower()
        title = prod_json['name']

        description = "<div>"
        descr = prod_json.get("description", "").replace("\n", "<br>")
        description += f'<div class="monotaro-descr">{descr}</div>'
        
        specifications, add_descr, weight_str, dims_str = self.get_specs("") # TODO
        if add_descr:
            description += self.parse_add_descr(add_descr)

        description += "</div>"
        # print(description+'\n')

        categories = None
        cat_list = [item['item']['name'] for item in bc_json.get('itemListElement', [{}])[1:]]
        if cat_list:
            categories = " > ".join(cat_list)
        
        vid_list = response.css('div.MovieContents__Iframe > iframe::attr(src)').getall()
        videos = ";".join(vid_list) if vid_list else None

        price = round(float(prod_json['offers']['price'])*self.JPY_TO_USD, 2)

        reviews = None
        rating = None
        if prod_json.get('aggregateRating'):
            reviews = prod_json['aggregateRating'].get('reviewCount', 0)
            rating = round(float(prod_json['aggregateRating'].get('ratingValue', 0.0)), 1)

        weight = self.get_weight(weight_str.lower()) if weight_str else None
        width, length, height = self.get_dims(dims_str.lower()) if dims_str else (None, None, None)

        yield {
            "date": datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
            "url": response.meta['url'],
            "source": "MonotaRO",
            "product_id": prod_id,
            "existence": existence,
            "title": prod_json['name'],
            "title_en": None,
            "description": description,
            "description_en": None,
            "summary": None,
            "sku": prod_id, # TODO
            "upc": None,
            "brand": prod_json.get('brand', {}).get('name'),
            "specifications": specifications,
            "categories": categories,
            "images": images,
            "videos": videos,
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
            "shipping_days_min": 1, # https://help.monotaro.com/app/answers/detail/a_id/13
            "shipping_days_max": 10,
            "weight": weight,
            "width": width,
            "length": length,
            "height": height
        }
