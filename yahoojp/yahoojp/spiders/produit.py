import json
import re
from datetime import datetime

import requests
import scrapy
from scrapy.http import HtmlResponse
from scrapy.selector import SelectorList


# scrapy crawl yahoojp_produit -O yahoojp_produits.json
class YahoojpProduit(scrapy.Spider):
    name = "yahoojp_produit"
    allowed_domains = ["store.shopping.yahoo.co.jp", "lohaco.yahoo.co.jp"]
    start_urls = []

    FILTERS = ['instabaner', 'instagram', 'tenbai', 'delivery', 'haisou', 'gift',
               'info', 'invoice', 'hoshou', 'bunkatsu','attention', 'yamato_huru',
               'tyuui', '1000en', 'tyui', 'hosyo', 'shouhou', 'campain', 'hatubai',
               'yupake', 'marketsale', 'matomegai', 'zcshpsl', 'zcsbzt', 'sale',
               'campaign', 'yohida', 'nekoposu', 'setsumei', 'takuhai', 'oshirase',
               'line_', 'alt="line"', '_line', 'yahoolinebana', '定期購入', '保証']

    CM_TO_IN = 0.393701
    G_TO_LB = 0.002205
    KG_TO_LB = 2.20462
    M_TO_IN = 39.37008
    MM_TO_IN = 0.03937

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
            "https://lohaco.yahoo.co.jp/store/h-lohaco/item/re41648",
            "https://lohaco.yahoo.co.jp/store/h-lohaco/item/wx88723",
            "https://lohaco.yahoo.co.jp/store/h-lohaco/item/hk77293",
            "https://lohaco.yahoo.co.jp/store/h-lohaco/item/rk84669",
            "https://lohaco.yahoo.co.jp/store/h-lohaco/item/hn23157",
            "https://lohaco.yahoo.co.jp/store/h-lohaco/item/6120688",
            "https://lohaco.yahoo.co.jp/store/h-lohaco3/item/p827709",
            "https://lohaco.yahoo.co.jp/store/h-lohaco/item/ju16176",
            "https://lohaco.yahoo.co.jp/store/h-lohaco/item/hn23160",
            "https://lohaco.yahoo.co.jp/store/h-lohaco/item/ee74357"
        ] # 测试用
        # with open('yahoojp_prods_urls.json', 'r', encoding='utf-8') as f_in:
        #     self.start_urls = [prod for prod in json.load(f_in)]
        # print(f"Total {len(self.start_urls):_} produit(s)".replace('_', '.'))

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
                                     callback=self.locaho_parse)
            else:
                yield scrapy.Request(url, headers=self.headers,
                                     meta={ 'url': url },
                                     callback=self.parse)

    def locaho_parse_descr(self, descr_txt: str, tag: str = 'div'):
        return f'<{tag} class="yahoojp-descr">{descr_txt}</{tag}>' if descr_txt else ''

    def locaho_parse_specs(self, nuxt: str):
        '''
        locaho：用正规表达式从页面中提取参数
        '''

        specs_info = {
            "more_descr": '',
            "upc": None,
            "specifications": None,
            "weight": None,
            "length": None,
            "width": None,
            "height": None
        }

        if not nuxt:
            return specs_info
        
        match1 = re.findall(r'specList\s*:\s*{\s*items\s*:(\[\s*[^\[\]]*\s*\])\s*}', nuxt)
        if not match1:
            return specs_info
        match2 = re.findall(r'{\s*name\s*:\s*"([^"]*)"\s*,\s*value\s*:\s*"([^"]*)"\s*}', match1[0])
        if not match2:
            return specs_info
        
        specs = []
        for si in match2:
            k, v = si

            if ('返品' in k) or (k == '備考'):
                continue  
            if (k == '使用方法') or ('注意事項' in k) or (('内容' in k) and ('内容量' not in k)) or ('成分' in k) or ('詳細' in k):
                specs_info['more_descr'] += f'<tr><th>{k}</th><td>{v}</td></tr>'
            else:
                specs.append({
                    "name": k,
                    "value": v
                })
                specs_info['specifications'] = specs if specs else None

                if k == 'JANコード':
                    specs_info['upc'] = v
                elif '内容量' in k: # TODO: 由参数解析尺寸
                    pass
                elif (k == '寸法') or (k == 'サイズ'):
                    pass

        return specs_info

    def locaho_parse_images(self, img_list: SelectorList):
        if not img_list:
            return None

        return ";".join([img.css('::attr(src)').get() for img in img_list])

    def locaho_parse_video(self, vid_sel: SelectorList):
        if not vid_sel:
            return None

        return vid_sel.css('::attr(src)').get()

    def locaho_parse_recensions(self, recens: dict):
        return (
            int(recens['reviewCount']) if recens.get('reviewCount') else None,
            float(recens['ratingValue']) if recens.get('ratingValue') else None
            )

    def locaho_parse_ship_fee(self, deliv_text: str, price_jpy: int):
        if not deliv_text:
            return 0.00

        # https://lohaco.yahoo.co.jp/help/delivery/#par_guidewysiwyg_13
        if '直送品グループ' in deliv_text:
            if price_jpy >= 1900:
                return 0.00
            return round(220/self.exch_rate, 2)
        else:
            if price_jpy >= 3780:
                return 0.00
            return round(550/self.exch_rate, 2)

    def locaho_parse_ship_day(self, day_text: str):
        if not day_text:
            return None

        if '翌日' in day_text:
            return 1
        return None

    def locaho_parse(self, response: HtmlResponse):
        url = response.meta['url']
        product_id = url.split('/')[-1]

        images = self.locaho_parse_images(response.css('div.thumbs img'))
        if not images:
            return

        scripts = response.css('script[type="application/ld+json"]')
        prod_json = None
        cat_json = None
        for scr in scripts:
            scr_text = scr.css('::text').get()
            if '"Product"' in scr_text:
                prod_json = json.loads(scr_text)
            elif '"BreadcrumbList"' in scr_text:
                cat_json = json.loads(scr_text)
            if prod_json and cat_json:
                break
        if not prod_json:
            return
        if not cat_json:
            cat_json = {}

        existence = ('instock' in prod_json['offers']['availability'].lower())

        nuxt = ''
        for scr in response.css('script').getall():
            if '__NUXT__' in scr:
                nuxt = scr
                break
        specs_info = self.locaho_parse_specs(nuxt)

        descr1 = self.locaho_parse_descr(prod_json["description"])
        descr2 = self.locaho_parse_descr(specs_info['more_descr'], 'table')
        description = descr1+descr2 if descr1+descr2 else None

        brand = (prod_json['brand'] if prod_json['brand'] else {}).get('name')
        categories = " > ".join([cat["name"] for cat in cat_json.get('itemListElement')[1:-1]])
        video = self.locaho_parse_video(response.css('div.extYouTube a'))
        price_jpy = prod_json['offers']['price']

        recens = prod_json['aggregateRating'] if prod_json.get('aggregateRating') else {}
        reviews, rating = self.locaho_parse_recensions(recens)

        shipping_fee = 0.00
        shipping_days_min = None
        ship_texts = response.css('div.mb-2 > p.black--text')
        if ship_texts:
            shipping_fee = self.locaho_parse_ship_fee(ship_texts.get(''), price_jpy)
        if len(ship_texts) >= 2:
            shipping_days_min = self.locaho_parse_ship_day(ship_texts[1].get())

        yield {
            "date": datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
            "url": url,
            "source": "Yahoo! JAPAN",
            "product_id": product_id,
            "existence": existence,
            "title": prod_json['name'],
            "title_en": None,
            "description": description,
            "description_en": None,
            "summary": None,
            "sku": product_id,
            "upc": specs_info['upc'],
            "brand": brand if brand else None,
            "specifications": specs_info['specifications'],
            "categories": categories,
            "images": images,
            "videos": video,
            "price": round(price_jpy/self.exch_rate, 2),
            "available_qty": 0 if not existence else None,
            "options": None, # 所谓变种实际上商品ID不同
            "variants": None,
            "has_only_default_variant": True,
            "returnable": False,
            "reviews": reviews,
            "rating": rating,
            "sold_count": None,
            "shipping_fee": shipping_fee,
            "shipping_days_min": shipping_days_min,
            "shipping_days_max": None,
            "weight": specs_info['weight'],
            "length": specs_info['length'],
            "width": specs_info['width'],
            "height": specs_info['height']
        }

    def parse_images(self, img_list: list):
        if not img_list:
            return None

        return ";".join([img['src'] for img in img_list if img['src'].startswith('https://item-')])

    def parse_descr(self, raw_descr: str):
        if not raw_descr:
            return ''

        # 过滤配送、转卖、店铺Instagram等无用资料
        resp_tmp = HtmlResponse('', body=f'<div id="temp">{raw_descr}</div>', encoding='utf-8')
        resp_getall = resp_tmp.css('div#temp > *, div#temp::text').getall() # 获得所有子要素和文字

        descr = ""
        for r in resp_getall:
            filter = False
            if ('<img ' in r):
                for f in self.FILTERS:
                    if f in r.lower():
                        filter = True
                        break
            if not filter:
                descr += r

        return f'<div class="yahoojp-descr">{descr}</div>' if descr else ''

    def parse_specs(self, specs_list: list):
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

        return " > ".join([cat['name'] for cat in cats_list])

    def parse_opts_vars(self, opts_list: list, vars_list: list, price_base: int, seller_id: str):
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
                    opts_charge_maps[f'{opt["name"]}:{ch["name"]}'] = ch["charge"] if ch["charge"] else 0

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

                    price += opts_charge_maps[f'{v["name"]}:{v["choiceName"]}']

                var_img = None
                if var['image']:
                    img_info = var['image']
                    if img_info['type'] == 'Item':
                        var_img = 'https://item-shopping.c.yimg.jp/i/n/'+img_info['id']
                    elif img_info['type'] == 'Lib':
                        var_img = f'https://shopping.c.yimg.jp/lib/{seller_id}/{img_info["id"]}'

                variants.append({
                    "variant_id": var['skuId'],
                    "barcode": None,
                    "sku": var['skuId'],
                    "option_values": option_values,
                    "images": var_img,
                    "price": round(price/self.exch_rate, 2),
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
        prod_scr = json.loads(prod_scr)['props']['pageProps']

        item = prod_scr['item']
        review = prod_scr['review'].get('reviewSummary', {})

        images = self.parse_images((item['images'] if item.get('images') else {}).get('displayItemImageList', []))
        if not images:
            print("No image:", url)
            return

        now = datetime.now()
        seller_id = prod_scr['seller']['id']
        product_id = item['srid']
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
        opts_vars = self.parse_opts_vars(item['individualItemOptionList'], item['individualItemList'], price_jpy, seller_id)

        yield {
            "date": now.strftime('%Y-%m-%dT%H:%M:%S'),
            "url": url,
            "source": "Yahoo! JAPAN",
            "product_id": product_id,
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
            "shipping_fee": round(prod_scr['postage'].get('fee', 0.00)/self.exch_rate, 2),
            "shipping_days_min": self.parse_deliv_date(item['delivery'], now),
            "shipping_days_max": None,
            "weight": spec_info['weight'],
            "length": None,
            "width": None,
            "height": None,
        }
