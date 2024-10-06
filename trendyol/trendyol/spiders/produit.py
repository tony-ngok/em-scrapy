import json
import re
from datetime import datetime

import requests
import scrapy
from scrapy.http import HtmlResponse
from scrapy.selector import SelectorList


# scrapy crawl trendyol_produit -O trendyol_produits.json # 复写整个数据
# scrapy crawl trendyol_produit -o trendyol_produits.json # 不复写
class TrendyolProduit(scrapy.Spider):
    name = 'trendyol_produit'
    allowed_domains = ['www.trendyol.com', 'apigw.trendyol.com']
    start_urls = []

    CM_TO_IN = 0.393701
    G_TO_LB = 0.002205
    KG_TO_LB = 2.20462
    M_TO_IN = 39.37008

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # self.start_urls = [
        #     'https://www.trendyol.com/bubito/kislik-tatli-kapsonlu-bebek-pelus-welsoft-tulum-p-446949530',
        #     'https://www.trendyol.com/sihhat-pharma/sihhat-aqua-beyaz-vazelin-50-ml-p-51920806',
        #     'https://www.trendyol.com/the-fine-organics/avustralya-nanesi-aktif-karbon-dis-beyazlatma-tozu-50g-p-762586955',
        #     'https://www.trendyol.com/l-oreal-paris/panorama-hacim-veren-maskara-koyu-kahverengi-p-796043319',
        #     'https://www.trendyol.com/oxvin/walker-baggy-bol-paca-2-iplik-orta-kalinlikta-uzun-esofman-alti-orijinal-kalip-p-855410433',
        #     'https://www.trendyol.com/oxvin/walker-baggy-bol-paca-2-iplik-orta-kalinlikta-uzun-esofman-alti-orijinal-kalip-p-855410436',
        #     'https://www.trendyol.com/mert-sert-mobilya/vern-120cm-konsol-tv-sehpasi-tv-unitesi-kahve-kosesi-banyo-dolabi-cok-amacli-dolap-p-773280008',
        #     'https://www.trendyol.com/bioderma/sebium-foaming-gel-karma-yagli-ve-akne-egilimli-ciltler-icin-yuz-temizleme-jeli-500-ml-p-132469',
        #     'https://www.trendyol.com/copierbond/ve-ge-a4-fotokopi-kagidi-80-g-500-lu-5-paket-2500ad-1-koli-p-6026206'
        # ]
        
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "fr-FR,fr;q=0.8,en-GB;q=0.5,en;q=0.3",
            "Connection": "keep-alive",
            "Priority": "u=0, i",
            "Referer": "https://www.google.com.tr/",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0"
        }

        with open('coursi.json', 'r', encoding='utf-8') as f_in:
            self.start_urls = [prod['prod_url'] for prod in json.load(f_in)]
        print(f"Total {len(self.start_urls):_} produit(s)".replace('_', '.'))

        exch = requests.get('https://open.er-api.com/v6/latest/USD')
        try:
            if exch.status_code in range(200, 300):
                exch_data = exch.json()
                self.exch_rate = exch_data['rates']['TRY']
                print("Get USD/TRY")
            else:
                raise Exception("Get USD/TRY: error", exch.status_code)
        except Exception as e:
            print(str(e))
            self.exch_rate = 34.27608
        finally:
            print(f"USD/TRY: {self.exch_rate}".replace('.', ','))

    def start_requests(self):
        for i, url in enumerate(self.start_urls, start=1):
            print(url, f"({i:_}/{len(self.start_urls):_})".replace("_", "."))
            yield scrapy.Request(url, headers=self.headers,
                                    meta={ "url": url },
                                    callback=self.parse)

    def get_json(self, response: HtmlResponse):
        '''
        获得重要数据聚集的JSON
        '''

        scrs = response.css('script[type="application/javascript"]')

        prod_json = None
        for scr in scrs:
            scr_txt = scr.css('::text').get('').strip()

            json_match = re.findall(r'__PRODUCT_DETAIL_APP_INITIAL_STATE__=(\{.*\});', scr_txt)
            if json_match:
                prod_json = json.loads(json_match[0])['product']
                break
        
        return prod_json

    def parse_descr_info(self, descr_info: list):
        '''
        提取JSON中的描述
        '''

        if not descr_info:
            return ''

        descr_txt = ""
        for descr in descr_info:
            if descr['priority'] == 0:
                descr_txt += f'<li>{descr["text"]}</li>'
        
        return f'<ul class="trendyol-descr">{descr_txt}</ul>' if descr_txt else ''

    def parse_var_info(self, var_info: list):
        '''
        从商品JSON的```variant```项中提取有用资料
        '''

        var_item = var_info[0]
        
        upc = var_item.get('barcode')
        available_qty = var_item.get('stock')

        option_name = var_item.get('attributeName')
        options = [{
            "id": var_item.get('attributeId'),
            "name": option_name
        }] if option_name else None

        return {
            "upc": upc,
            "available_qty": available_qty,
            "options": options
        }

    def parse_specs(self, specs_infos: list):
        '''
        由JSON解析参数
        '''

        if not specs_infos:
            return {
                "specifications": None,
                "weight": None,
                "length": None,
                "width": None,
                "height": None
            }

        specs = []
        weight = None
        length = None
        width = None
        height = None
        for spec in specs_infos:
            k = spec['key']['name']
            v = spec['value']['name']
            specs.append({
                "name": k,
                "value": v
            })

            kk = k.lower()
            vv = v.lower()
            if ('gramaj' in kk) or ('hacim' in kk) or ('ağırlık' in kk):
                weight = self.get_dim(vv, r'(\d+(?:\.\d+)?)\s?(g|kg|ml|l|cc|gr)\b')
            elif ('derinlik' in kk):
                length = self.get_dim(vv, r'(\d+(?:\.\d+)?)\s?(m|cm)\b')
            elif ('genişlik' in kk):
                width = self.get_dim(vv, r'(\d+(?:\.\d+)?)\s?(m|cm)\b')
            elif ('yükseklik' in kk):
                height = self.get_dim(vv, r'(\d+(?:\.\d+)?)\s?(m|cm)\b')
        
        return {
            "specifications": specs if specs else None,
            "weight": weight,
            "length": length,
            "width": width,
            "height": height
        }
    
    def parse_cats(self, cats_infos: SelectorList):
        '''
        由JSON解析分类
        '''

        if not cats_infos:
            return None
        
        return " > ".join([cat.css('::text').get().strip() for cat in cats_infos])

    def parse_vars(self, opt_info: list, vars_infos: list):
        '''
        由JSON解析商品变种（有变种的商品选项都只有一个）
        '''

        if not (opt_info and vars_infos):
            return None

        return [{
            "variant_id": str(vi['itemNumber']),
            "barcode": vi['barcode'],
            "sku": '',
            "option_values": [{
                "option_id": str(opt_info[0]['id']),
                "option_value_id": None,
                "option_name": opt_info[0]['name'],
                "option_value": vi['value']
            }],
            "images": None,
            "price": round(vi['price']/self.exch_rate, 2),
            "available_qty": 0 if not vi['inStock'] else None
        } for vi in vars_infos]

    def get_dim(self, txt: str, regex: str):
        '''
        商品重量、尺寸
        '''

        dim_match = re.findall(regex, txt)
        if dim_match:
            val = float(dim_match[0][0])
            unit = dim_match[0][1]

            if unit in {'kg', 'l'}:
                return round(val*self.KG_TO_LB, 2)
            if unit in {'g', 'ml', 'cc', 'gr'}:
                return round(val*self.G_TO_LB, 2)
            if unit == 'm':
                return round(val*self.M_TO_IN, 2)
            if unit == 'cm':
                return round(val*self.CM_TO_IN, 2)

    def parse(self, response: HtmlResponse):
        url = response.meta['url']
        
        prod_json = self.get_json(response)
        if not prod_json:
            print("No product JSON:", url)
            return

        img_list = prod_json.get('images')
        if not img_list:
            print("No images:", url)
            return
        
        price_raw = prod_json.get('price', {}).get('sellingPrice', {}).get('value')
        if price_raw is None:
            print("No price:", url)
            return
        price = round(price_raw/self.exch_rate, 2)
        
        product_id = str(prod_json['id'])
        existence = prod_json['hasStock'] and prod_json['isSellable']
        descr_info = self.parse_descr_info(prod_json.get('descriptions', []))
        has_more_descr = prod_json.get('hasHtmlContent', False)
        spec_info = self.parse_specs(prod_json.get('attributes', []))
        video_id = prod_json.get('merchant', {}).get('videoContentId')

        var_info = prod_json.get('variants')
        var_parse = self.parse_var_info(var_info if var_info else [{}])

        brand_info = prod_json.get('brand', {})
        brand = brand_info['name'] if brand_info.get('name') else None

        cats_list = response.css('div#marketing-product-detail-breadcrumb a.product-detail-breadcrumb-item > span')[1:-1]
        categories = self.parse_cats(cats_list)

        options = var_parse['options'] # 单一选项名
        variants = self.parse_vars(options, prod_json.get('allVariants'))
        
        recension = prod_json.get('ratingScore', {})
        reviews = recension.get('totalRatingCount')
        rating = recension.get('averageRating')

        item = {
            "date": datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
            "url": url,
            "source": "Trendyol",
            "product_id": product_id,
            "existence": existence,
            "title": prod_json['name'],
            "title_en": None,
            "description": descr_info, # 稍后会变
            "description_en": None,
            "summary": None,
            "sku": product_id,
            "upc": var_parse['upc'],
            "brand": brand,
            "specifications": spec_info['specifications'],
            "categories": categories,
            "images": ";".join(["https://cdn.dsmcdn.com/"+img for img in img_list]),
            "videos": None, # 稍后会变
            "price": price,
            "available_qty": var_parse['available_qty'] if existence else 0,
            "options": options,
            "variants": variants,
            "has_only_default_variant": not (variants and len(variants) > 1),
            "returnable": False,
            "reviews": reviews,
            "rating": rating,
            "sold_count": None,
            "shipping_fee": 0.00 if prod_json.get('isFreeCargo') or (price >= 200*self.exch_rate) else round(34.99/self.exch_rate, 2), # https://www.trendyol.com/yardim/sorular/2002?grup=1
            "shipping_days_min": None,
            "shipping_days_max": None,
            "weight": spec_info['weight'],
            "length": spec_info['length'],
            "width": spec_info['width'],
            "height": spec_info['height']
        }

        if has_more_descr:
            descr_api = f'https://apigw.trendyol.com/discovery-web-productgw-service/api/product-detail/{product_id}/html-content?channelId=1'
            headers = { **self.headers, 'Referer': url }
            yield scrapy.Request(descr_api, headers=headers,
                                 meta={
                                     "item": item,
                                     "video_id": video_id
                                 },
                                 callback=self.parse_descr_page)
        elif video_id:
            item['description'] = descr_info if descr_info else None
            video_api = f'https://apigw.trendyol.com/discovery-web-websfxmediacenter-santral/video-content-by-id/{video_id}?channelId=1'
            headers = { **self.headers, 'Referer': url }
            yield scrapy.Request(video_api, headers=headers,
                                 meta={
                                     "item": item,
                                 },
                                 callback=self.parse_video)
        else:
            item['description'] = descr_info if descr_info else None
            yield item

    def parse_descr_page(self, response: HtmlResponse):
        item = response.meta['item']
        url = item['url']
        descr_info = item['description']
        video_id = response.meta['video_id']

        descr_page = response.json()['result']
        descr_page = '' if not descr_page else '<div class="trendyol-descr">'+descr_page.strip().replace("\n", "")+'</div>'

        description = descr_info+descr_page
        item['description'] = description if description else None
        
        if video_id:
            video_api = f'https://apigw.trendyol.com/discovery-web-websfxmediacenter-santral/video-content-by-id/{video_id}?channelId=1'
            headers = { **self.headers, 'Referer': url }
            yield scrapy.Request(video_api, headers=headers,
                                 meta={
                                     "item": item,
                                 },
                                 callback=self.parse_video)
        else:
            yield item
    
    def parse_video(self, response: HtmlResponse):
        item = response.meta['item']
        item['videos'] = response.json().get('result', {}).get('url')
        yield item
