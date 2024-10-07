import json
import re
from datetime import datetime

import requests
import scrapy
from scrapy.http import HtmlResponse


# scrapy crawl yahoojp_produit -O yahoojp_produits.json
class YahoojpProduit(scrapy.Spider):
    name = "yahoojp_produit"
    allowed_domains = ["store.shopping.yahoo.co.jp", "lohaco.yahoo.co.jp"]
    start_urls = []

    FILTERS = ['/instabaner.', '/yahoo-instagram-banner.', 'tenbai', 'delivery', 'haisou']

    # CM_TO_IN = 0.393701
    G_TO_LB = 0.002205
    KG_TO_LB = 2.20462
    # M_TO_IN = 39.37008
    # MM_TO_IN = 0.03937

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "fr-FR,fr;q=0.9,en-GB;q=0.8,en;q=0.7",
            "dnt": "1",
            "priority": "u=0, i",
            "referer": "https://shopping.yahoo.co.jp/",
            "sec-ch-ua": '"Microsoft Edge";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            "sec-ch-ua-arch": '"x86"',
            "sec-ch-ua-full-version-list": '"Microsoft Edge";v="129.0.2792.65", "Not=A?Brand";v="8.0.0.0", "Chromium";v="129.0.6668.71"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-model": '""',
            "sec-ch-ua-platform": '"Windows"',
            "sec-ch-ua-platform-version": '"10.0.0"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0"
        }

        self.start_urls = [
            "https://store.shopping.yahoo.co.jp/kscojp/403411141-1.html",
            "https://store.shopping.yahoo.co.jp/kscojp/590632062-2.html",
            "https://store.shopping.yahoo.co.jp/shizenshop/cocosilk-haircap-long45r.html",
            "https://store.shopping.yahoo.co.jp/elpisstore/r356.html",
            # "https://lohaco.yahoo.co.jp/store/h-lohaco/item/re41648",
            "https://store.shopping.yahoo.co.jp/lifeessence/vcl.html",
            # "https://lohaco.yahoo.co.jp/store/h-lohaco/item/wx88723",
            "https://store.shopping.yahoo.co.jp/mygift/yunth-sk-4580785290040.html",
            "https://store.shopping.yahoo.co.jp/kscojp/669042492-hnd.html",
            "https://store.shopping.yahoo.co.jp/kisekiforyou/kissme-sk-4901433038492.html",
            "https://store.shopping.yahoo.co.jp/kisocare/kiso-k35.html"
        ] # 测试用

        exch = requests.get('https://open.er-api.com/v6/latest/USD')
        try:
            if exch.status_code in range(200, 300):
                exch_data = exch.json()
                self.exch_rate = exch_data['rates']['JPY']
                print("Get USD/JPY")
            else:
                raise Exception("Get USD/JPY: error", exch.status_code)
        except Exception as e:
            print(str(e))
            self.exch_rate = 148.627695
        finally:
            print(f"USD/JPY: {self.exch_rate}".replace('.', ','))

    def start_requests(self):
        for i, url in enumerate(self.start_urls, start=1):
            print(f"{i:_}/{len(self.start_urls):_}".replace("_", "."), url)

            if url.startswith('https://lohaco'):
                yield scrapy.Request(url, headers=self.headers,
                                     meta={ 'url': url },
                                     callback=self.parse_lohaco)
            else:
                yield scrapy.Request(url, headers=self.headers,
                                     meta={ 'url': url },
                                     callback=self.parse)

    def parse_lohaco(self, response: HtmlResponse):
        url = response.meta['url']
    
    def parse_images(self, img_list: list):
        if not img_list:
            return None
        
        return ";".join([img['src'] for img in img_list if img['src'].startswith('https://item-')])

    def parse_descr(self, raw_descr: str): # TODO
        if not raw_descr:
            return ''



        return ''

    def parse_specs(self, specs_list: list): # TODO
        specifications = []
        weight = None

        if specs_list:
            for sp in specs_list:
                spec = {
                    "name": sp['name'],
                    "value": ";".join([v['name'] for v in sp['valueList']])
                }
                specifications.append(spec)
            
                if ('内容量' in sp['name']) and (weight is None):
                    weight = self.get_dim(spec['value'].lower(), r'(\d+(?:\.\d+)?)\s?(g|kg|ml|l)\b')

        return {
            "specifications": specifications if specifications else None,
            "weight": weight
        }
    
    def parse_cats(self, cats_list: list):
        if not cats_list:
            return None
        
        return [cat['name'] for cat in cats_list]

    def parse_opts_vars(self, opts_list: list, vars_list: list, price_base: int):
        options = []
        opts_charge_maps = {}
        variants = []

        if (opts_list and vars_list):
            for opt in opts_list:
                options.append({
                    "id": None,
                    "name": opt['name']
                })

                for ch in opt['choiceList']:
                    opts_charge_maps[f'{opt['name']}:{ch['name']}'] = ch['charge'] if ch['charge'] else 0


            for var in vars_list:
                price = price_base

                option_values = []
                for v in var['optionList']:
                    option_values.append({
                        "option_id": None,
                        "option_value_id": None,
                        "option_name": v['name'],
                        "option_value": v['choiceName']
                    })

                    price += opts_charge_maps[f'{v['name']}:{v['choiceName']}']
        
                variants.append({
                    "variant_id": var['skuId'],
                    "barcode": None,
                    "sku": var['skuId'],
                    "option_values": option_values,
                    "images": var['image'],
                    "price": float(price/self.exch_rate, 2),
                    "available_qty": var['stock'].get('quantity')
                })

        return {
            "options": options if options else None,
            "variants": variants if variants else None
        }

    def parse_deliv_date(self, deliv_infos: dict, actual: datetime):
        if not (deliv_infos and deliv_infos.get('hasDeliveryDate') and deliv_infos.get('methodList')):
            return None
        
        deliv_date = deliv_infos.get('methodList')[0].get('shortestDate')
        if not deliv_date:
            return None
        
        diff = (datetime.strptime(deliv_date, '%Y%m%d')-actual).days
        return diff if diff > 0 else 0
    
    def get_dim(self, txt: str, regex: str):
        dim_match = re.findall(regex, txt)
        if dim_match:
            val = float(dim_match[0][0])
            unit = dim_match[0][1]

            if unit in {'kg', 'l'}:
                return round(val*self.KG_TO_LB, 2)
            if unit in {'g', 'ml'}:
                return round(val*self.G_TO_LB, 2)
            # if unit == 'm':
            #     return round(val*self.M_TO_IN, 2)
            # if unit == 'cm':
            #     return round(val*self.CM_TO_IN, 2)

    def parse(self, response: HtmlResponse):
        url = response.meta['url']

        prod_scr = response.css('script#__NEXT_DATA__::text').get('').strip()
        if not prod_scr:
            return
        prod_scr = json.loads(prod_scr)
        
        item = prod_scr['item']
        review = prod_scr['review'].get('reviewSummary', {})

        images = self.parse_images((item['images'] if item.get('images') else {}).get('displayItemImageList', []))
        if not images:
            print("No image:", url)
            return

        now = datetime.now()
        product_id = prod_scr['srid']
        existence = item['stock']['isAvailable']

        brand = None
        if item['brandName'] and (item['brandName'] != 'ブランド登録なし'):
            brand = item['brandName']

        descr0 = self.parse_descr(item['information'])
        descr1 = self.parse_descr(item['freeSpace1'])
        descr2 = self.parse_descr(item['freeSpace2'])
        descr3 = self.parse_descr(item['freeSpace3'])
        descr4 = self.parse_descr(item['caption'])
        description = descr0+descr1+descr2+descr3+descr4

        spec_info = self.parse_specs(item['specList'])
        categories = self.parse_cats((item['genreCategory'] if item.get('genreCategory') else {}).get('categoryPathsIgnoreShopping', []))
        price_jpy = item['applicablePrice']
        opts_vars = self.parse_opts_vars(item['individualItemOptionList'], item['individualItemList'], price_jpy)

        yield {
            "date": now.strftime('%Y-%m-%dT%H:%M:%S'),
            "url": url,
            "source": "Yahoo! JAPAN",
            "product_id": prod_scr['srid'],
            "existence": existence,
            "title": item['name'],
            "title_en": None,
            "description": description if description else None,
            "description_en": None,
            "summary": None,
            "sku": product_id,
            "upc": item['janCode'] if item['janCode'] else None,
            "brand": brand,
            "specifications": spec_info['specifications'],
            "categories": categories,
            "images": images,
            "videos": None,
            "price": round(price_jpy/self.exch_rate, 2),
            "available_qty": 0 if not existence else item['stock'].get('quantity'),
            "options": opts_vars['options'],
            "variants": opts_vars['variants'],
            "has_only_default_variant": not (opts_vars['variants'] and (len(opts_vars['variants']) > 1)),
            "returnable": False,
            "reviews": review.get('count'),
            "rating": review.get('average'),
            "sold_count": None,
            "shipping_fee": float(prod_scr['postage'].get('fee', 0.00)/self.exch_rate, 2),
            "shipping_days_min": self.parse_deliv_date(item['delivery']),
            "shipping_days_max": None,
            "weight": spec_info['weight'],
            "length": None,
            "width": None,
            "Height": None,
        }
