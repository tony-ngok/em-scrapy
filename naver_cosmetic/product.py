import json
import re
import sys
import time
from datetime import datetime
from random import randint

import requests
from scrapy.http import HtmlResponse


class NaverCosmeticProduct:
    HEADERS = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "de-DE,de;q=0.9,en-GB;q=0.8,en;q=0.7",
        "dnt": "1",
        "priority": "u=0, i",
        "referer": "https://shopping.naver.com/",
        "sec-ch-ua": "\"Microsoft Edge\";v=\"129\", \"Not=A?Brand\";v=\"8\", \"Chromium\";v=\"129\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Yeti/1.1; +https://naver.me/spd) Chrome/106.0.5249.0 Safari/537.36" # https://seoapi.com/naverbot/
    }

    # 若描述图片文件名中包含以下字样，则过滤掉
    DESC_IMG_FILTER = [
        "%EC%BF%A0%ED%8F%B0", "%ED%95%A0%EC%9D%B8", "%EC%8A%88%ED%8D%BC%EB%94%9C",
        "%EB%B0%B0%EB%84%88", "%EC%95%88%EB%82%B4", "%EB%B0%B0%EC%86%A1",
        "%EA%B3%B5%EC%8B%9D", "%EC%9D%B8%ED%8A%B8%EB%A1%9C", "%ED%95%98%EB%8B%A8",
        "%EB%AA%A8%EB%93%A0%EC%A0%9C%ED%92%88"
    ]

    def __init__(self, mode: str = 'cosmetic', review: bool = False, todos: list = []):
        self.mode = mode
        self.review = review
        self.dones = 0
        self.todos = []

        if self.review:
            try:
                with open(f'naver_{mode}_prods.txt', 'r', encoding='utf-8') as f_prods:
                    for _ in f_prods:
                        self.dones += 1
            except:
                print("No existents product(s)")
                self.review = False
                for todo in todos:
                    self.todos.append(todo)

            try:
                with open(f'naver_{mode}_prods_errs.txt', 'r', encoding='utf-8') as f_errs:
                    for line in f_errs:
                        self.todos.append(line.strip())
            except:
                print("No prev(s) err(s)")
        else:
            print("Start anew")
            for todo in todos:
                self.todos.append(todo)

        print(f"{self.dones:_} existent product(s)".replace('_', '.'))
        print(f"{len(self.todos):_} URL(s) todo".replace('_', '.'))

        self.errs = 0
        self.get_rate()

    def get_rate(self):
        try:
            rate_resp = requests.get('https://open.er-api.com/v6/latest/USD', timeout=10, allow_redirects=False)
            if rate_resp.status_code >= 300:
                raise Exception()

            print("Get USD/KRW rate")
            self.krw_rate = rate_resp.json()['rates']['KRW']
        except:
            print("Fail to get USD/KRW rate")
            self.krw_rate = 1368.537958
        finally:
            print(f"USD/KRW rate: {self.krw_rate:_}".replace(".", ",").replace("_", "."))

    def count(self):
        print(f"{self.dones:_} existent product(s)".replace('_', '.'))
        print(f"{self.errs:_} err(s)".replace('_', '.'))

    def scrape(self):
        for i, todo in enumerate(self.todos, start=1):
            yield self.get_prod_info(i, todo)
            if i % 50 == 0:
                self.pause(10)

    def get_exist(self):
        return (not self.prod_json['soldout'])

    def pause(self, secs: int):
        for s in range(secs, 0, -1):
            print(f"PAUSE: {s:03d}", end='\r')
            time.sleep(1)

    def get_div_descr(self, prod_id: str):
        desc_url = f'https://shopping.naver.com/product-detail/v1/products/{prod_id}/contents/pc/PC'
        descr = ""

        j = 1
        descr_resp = requests.get(desc_url, headers=self.HEADERS, timeout=60, allow_redirects=False)
        while descr_resp.status_code >= 300:
            if descr_resp.status_code == 404:
                print("No div descriptions")
                return ""
            else:
                print(f"API call fail with status {descr_resp.status_code}: {desc_url} ({j}/10)")
                j += 1
                if j > 10:
                    raise Exception(f'Status {descr_resp.status_code}')
                self.pause(randint(90, 120))
                descr_resp = requests.get(desc_url, headers=self.HEADERS, timeout=60, allow_redirects=False)
        if descr_resp.status_code == 204:
            print("No div descriptions")
            return ""

        raw_descr = descr_resp.json()['renderContent']
        resp_tmp = HtmlResponse('', body=raw_descr, encoding='utf-8')
        resp_getall = resp_tmp.css('p > span, img')

        for sel in resp_getall:
            if sel.root.tag == 'span':
                span_txt = " ".join(sel.css('::text').get('').replace("\n", "").strip().split())
                if span_txt:
                    descr += f'<p>{span_txt}</p>'
            else:
                img_url = sel.css('::attr(data-src)').get()
                if not img_url:
                    continue

                filter = False
                for f in self.DESC_IMG_FILTER:
                    if f in img_url:
                        filter = True
                        break
                if not filter:
                    descr += f'<p><img src="{img_url}"></p>'

        return (f'<div class="naver-{self.mode}-descr">{descr}</div>' if descr else "")

    def get_table_descr(self):
        try:
            fields = self.prod_json['productInfoProvidedNoticeView']['basic']
            if fields:
                t_descr = ""
                for k, v in fields.items():
                    if ('보증' in k) or ('전화번호' in k) or ('판매업자' in k) or ('인증' in k) or ('A/S' in k):
                        continue

                    if isinstance(v, dict):
                        v1 = "<ul>"
                        for vk, vv in v.items():
                            vv = vv.replace("\n", "")
                            v1 += f"<li>{vk}: {vv}</li>"
                        v1 += "</ul>"
                    elif isinstance(v, list):
                        v1 = "<ul>"
                        for vk in v:
                            vk = vk.replace("\n", "")
                            v1 += f"<li>{vk}</li>"
                        v1 += "</ul>"
                    else:
                        v1 = v.replace("\n", "")

                    t_descr += f"<tr><th>{k}</th><td>{v1}</td></tr>"

                return (f'<table class="naver-{self.mode}-descr">{t_descr}</table>' if t_descr else "")
        except:
            pass

        return ""

    def get_specs(self):
        specs = []
        weight = None

        fields1 = self.prod_json.get('viewAttributes')
        if fields1:
            for k, v in fields1.items():
                if ('이벤트' in k) or ('사은품' in k):
                    continue
                specs.append({
                    "name": k,
                    "value": v
                })

        fields2 = self.prod_json.get('detailAttributes')
        if fields2:
            for k, v in fields2.items():
                specs.append({
                    "name": k,
                    "value": v
                })
                if ('용량' in k) or ('중량' in k):
                    weight = self.parse_weight(v.lower())

        return ((specs if specs else None), weight)

    def parse_weight(self, txt: str):
        weight_match = re.findall(r'(\d+(?:\.\d+)?)\s*(?:g|ml)', txt)
        if weight_match:
            return round(float(weight_match[0])/453.59237, 2)

    def get_cats(self):
        cats_txt = self.prod_json.get('category', {}).get('wholeCategoryName', '')
        if not cats_txt:
            return None
        return " > ".join(cats_txt.split(">"))

    def get_images(self):
        img_list = self.prod_json.get('productImages')
        if not img_list:
            return None
        return ";".join([img['url'] for img in img_list])

    def get_avail_qty(self, existence: bool):
        if not existence:
            return 0
        return self.prod_json.get('stockQuantity')

    def get_opts_vars(self, price_krw: int):
        has_opts = self.prod_json.get('optionUsable')
        if not has_opts:
            return (None, None)

        options = []
        variants = []

        opt_list = self.prod_json.get('options')
        if opt_list:
            opt_combos = self.prod_json.get('optionCombinations')
            if opt_combos: # 复合选项
                opt_list = list(filter(lambda opt: (opt['optionType'] == 'COMBINATION'), opt_list))
                if opt_list:
                    for opt in opt_list:
                        options.append({
                            "id": str(opt['id']),
                            "name": opt['groupName']
                        })

                    for oc in opt_combos:
                        opt_vals = []
                        for i, o in enumerate(options):
                            opt_vals.append({
                                "option_id": o['id'],
                                "option_value_id": None,
                                "option_name": o['name'],
                                "option_value": oc[f"optionName{i+1}"]
                            })
                        variants.append({
                            "variant_id": str(oc["id"]),
                            "barcode": None,
                            "sku": str(oc["id"]),
                            "option_values": opt_vals,
                            "images": None,
                            "price": round((price_krw+oc['price'])/self.krw_rate, 2),
                            "available_qty": oc['stockQuantity']
                        })
            else: # 单一选项
                opt_list = list(filter(lambda opt: (opt['optionType'] == 'SIMPLE'), opt_list))
                if opt_list:
                    opt_set = set()
                    for opt in opt_list:
                        opt_name = opt['groupName']
                        if opt_name not in opt_set:
                            opt_set.add(opt_name)
                            options.append({
                                "id": None,
                                "name": opt_name
                            })
                        variants.append({
                            "variant_id": str(opt["id"]),
                            "barcode": None,
                            "sku": str(opt["id"]),
                            "option_values": [{
                                "option_id": None,
                                "option_value_id": None,
                                "option_name": opt['groupName'],
                                "option_value": opt['name'],
                            }],
                            "images": None,
                            "price": round(price_krw/self.krw_rate, 2),
                            "available_qty": None
                        })

        return ((options if options else None), (variants if variants else None))

    def get_recensions(self):
        recens = self.prod_json.get('reviewAmount')
        if not recens:
            return (None, None)
        return (recens['totalReviewCount'], recens['averageReviewScore'])

    def get_deliv_fee(self):
        deliv_info = self.prod_json.get('productDeliveryInfo')
        if (not deliv_info) or (deliv_info['deliveryFeeType'].lower() == 'free'):
            return 0.00
        return round(deliv_info['baseFee']/self.krw_rate, 2)

    def get_deliv_days(self):
        try:
            deliv_txt = self.prod_json['productInfoProvidedNoticeView']['additional']['주문 이후 예상되는 배송기간']

            deliv_match1 = re.findall(r'(\d+)일 이내', deliv_txt)
            deliv_match2 = re.findall(r'(\d+)일 이상', deliv_txt)
            deliv_match3 = re.findall(r'(\d+)~(\d+)일', deliv_txt)
            deliv_match4 = re.findall(r'(\d+)일', deliv_txt)

            if deliv_match1:
                return (0, int(deliv_match1[0]))
            elif deliv_match2:
                return (int(deliv_match2[0]), None)
            elif deliv_match3:
                return (int(deliv_match3[0][0]), int(deliv_match3[0][1]))
            elif deliv_match4:
                return (int(deliv_match4[0]), int(deliv_match4[0]))
        except:
            pass

        return (None, None)

    def get_prod_info(self, i: int, prod_id: str):
        if self.mode == 'cosmetic':
            url = f'https://shopping.naver.com/shopv/v1/luxury/products/{prod_id}/detail?subVertical=COSMETIC'
        elif self.mode == 'logistics':
            url = f'https://shopping.naver.com/shopv/v1/logistics/products/{prod_id}/detail'
        print(f'\n{i:_}/{len(self.todos):_}'.replace("_", "."), url)

        try:
            j = 1
            resp = requests.get(url, headers=self.HEADERS, timeout=300, allow_redirects=False)
            while resp.status_code >= 300:
                if resp.status_code == 404:
                    print("Product not found")
                    return
                else:
                    print(f"API call fail with status {resp.status_code}: {url} ({j}/10)")
                    j += 1
                    if j > 10:
                        raise Exception(f'Status {resp.status_code}')
                    self.pause(randint(90, 120))
                    resp = requests.get(url, headers=self.HEADERS, timeout=300, allow_redirects=False)

            self.prod_json = resp.json()

            images = self.get_images()
            if not images:
                print("No images")
                return

            if self.mode == 'cosmetic':
                url_root = 'https://shopping.naver.com/luxury/cosmetic/products/'
            elif self.mode == 'logistics':
                url_root = 'https://shopping.naver.com/logistics/products/'

            existence = self.get_exist()
            time.sleep(randint(1000, 3000)/1000.0)
            description = self.get_div_descr(prod_id)+self.get_table_descr()
            specifications, weight = self.get_specs()
            price_krw = self.prod_json.get('discountedSalePrice', self.prod_json.get('salePrice', 0))
            options, variants = self.get_opts_vars(price_krw)
            reviews, rating = self.get_recensions()
            ship_dmin, ship_dmax = self.get_deliv_days()

            product = {
                "date": datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                "url": url_root+prod_id,
                "source": "Naver",
                "product_id": prod_id,
                "existence": existence,
                "title": self.prod_json['name'],
                "title_en": None,
                "description": (description if description else None),
                "description_en": None,
                "summary": None,
                "sku": prod_id,
                "upc": prod_id,
                "brand": (self.prod_json['brandStoreName'] if self.prod_json.get('brandStoreName') else None),
                "specifications": specifications,
                "categories": self.get_cats(),
                "images": images,
                "videos": None,
                "price": round(price_krw/self.krw_rate, 2),
                "available_qty": self.get_avail_qty(existence),
                "options": options,
                "variants": variants,
                "has_only_default_variant": not (variants and (len(variants) > 1)),
                "returnable": False,
                "reviews": reviews,
                "rating": rating,
                "sold_count": None,
                "shipping_fee": self.get_deliv_fee(),
                "shipping_days_min": ship_dmin,
                "shipping_days_max": ship_dmax,
                "weight": weight,
                "length": None,
                "width": None,
                "height": None
            }
            print(product)
            self.dones += 1
            self.count()
            time.sleep(randint(1000, 3000)/1000.0)
            return product
        except Exception as e:
            print("ERROR:", str(e))
            self.errs += 1
            self.count()
            self.pause(randint(90, 120))

            return prod_id

    def write_files(self): # TODO: 写入文件的函数
        mode = 'a' if self.review else 'w'
        with open(f'naver_{self.mode}_prods.txt', mode, encoding='utf-8') as f_prods, open(f'naver_{self.mode}_prods_errs.txt', 'w', encoding='utf-8') as f_errs:
            for y in self.scrape():
                if isinstance(y, dict):
                    json.dump(y, f_prods, ensure_ascii=False)
                    f_prods.write(',\n')
                elif isinstance(y, str): # 出错的商品号
                    f_errs.write(y+'\n')

        if self.errs:
            sys.exit(1)
        else:
            sys.exit(0)


if __name__ == '__main__':
    if (len(sys.argv) >= 2) and ((sys.argv[1] == 'cosmetic') or (sys.argv[1] == 'logistics')):
        review = False
        if (len(sys.argv) >= 3) and (sys.argv[2] == '--review'):
            review = True

        todos = []
        if not review:
            with open(f'naver_{sys.argv[1]}_prods_ids.txt', 'r', encoding='utf-8') as prods_ids:
                for line in prods_ids:
                    todos.append(line.strip())

        nc_recs = NaverCosmeticProduct(sys.argv[1], review, todos)
        nc_recs.write_files()
