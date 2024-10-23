# https://blog.naver.com/spson0153/223390335136

import asyncio
import json
import re
import sys
import time
from datetime import datetime
from random import randint

import requests
from pyppeteer import launch
from scrapy.http import HtmlResponse


class NaverHandmadeProduct:
    GET_ATTR_JS = '(elem, attr) => elem.getAttribute(attr)'
    GET_TXT_JS = '(elem) => elem.textContent'

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
        "user-agent": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Yeti/1.1; +https://naver.me/spd) Chrome/106.0.5249.0 Safari/537.36"
    }

    # 若描述图片文件名中包含以下字样，则过滤掉
    DESC_IMG_FILTER = [
        "%EC%BF%A0%ED%8F%B0", "%ED%95%A0%EC%9D%B8", "%EC%8A%88%ED%8D%BC%EB%94%9C",
        "%EB%B0%B0%EB%84%88", "%EC%95%88%EB%82%B4", "%EB%B0%B0%EC%86%A1",
        "%EA%B3%B5%EC%8B%9D", "%EC%9D%B8%ED%8A%B8%EB%A1%9C", "%ED%95%98%EB%8B%A8",
        "%EB%AA%A8%EB%93%A0%EC%A0%9C%ED%92%88"
    ]

    def __init__(self, review: bool = False, todos: list = []):
        self.review = review
        self.dones = 0
        self.todos = []

        if self.review:
            try:
                with open('naver_handmade_prods.txt', 'r', encoding='utf-8') as f_prods:
                    for _ in f_prods:
                        self.dones += 1
            except:
                print("No existents product(s)")
                self.review = False
                for todo in todos:
                    self.todos.append(todo)

            try:
                with open('naver_handmade_prods_errs.txt', 'r', encoding='utf-8') as f_errs:
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

    async def pause(self, secs: int):
        for s in range(secs, 0, -1):
            print(f"PAUSE: {s:03d}", end='\r')
            await asyncio.sleep(1)

    async def start(self):
        self.browser = await launch(headless=False)
        self.page = await self.browser.newPage()
        self.page.setDefaultNavigationTimeout(300000)
        await self.page.setViewport({ 'width': 1024, 'height': 768 })
        await self.page.setExtraHTTPHeaders(self.HEADERS)

    async def scrape(self):
        for i, todo in enumerate(self.todos, start=1):
            if i % 10 == 1:
                await self.start()

            start_time = time.time()
            yield await self.get_prod_info(i, todo)

            r = randint(10, 20)
            remain = int(r+start_time-time.time())
            if remain > 0:
                await self.pause(remain)

            if i % 10 == 0:
                await self.browser.close()
                await self.pause(10)

    async def get_basic_json(self):
        basic_json_sel = await self.page.querySelector('script[type="application/ld+json"]')
        basic_json_text = await self.page.evaluate(self.GET_TXT_JS, basic_json_sel)
        self.basic_json = json.loads(basic_json_text)

    async def get_var_json(self):
        var_json = None

        for scr in (await self.page.querySelectorAll('script')):
            scr_txt = (await self.page.evaluate(self.GET_TXT_JS, scr)).strip()
            if '__PRELOADED_STATE__' in scr_txt:
                var_json_match = re.findall(r'window.__PRELOADED_STATE__\s*=\s*(\{.+\})', scr_txt)
                if var_json_match:
                    var_json = json.loads(var_json_match[0])
                    break

        if 'product' in var_json:
            self.var_json = var_json['product']['A']
        elif 'productDetail' in var_json:
            self.var_json = var_json['productDetail']['A']['contents']

    def get_exist(self):
        return (not self.var_json['soldout']) and ('instock' in self.basic_json['offers']['availability'].lower())

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
                print(f"API call fail with status {descr_resp.status_code}: {desc_url} ({j}/5)")
                j += 1
                if j >= 5:
                    raise Exception(f'Status {descr_resp.status_code}')
                for s in range(120, 0, -1):
                    print(f"PAUSE: {s:03d}", end='\r')
                    time.sleep(1)
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

        return (f'<div class="naver-handmade-descr">{descr}</div>' if descr else "")

    def get_table_descr(self):
        try:
            fields = self.prelJson['productInfoProvidedNoticeView']['basic']
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

                return (f'<table class="naver-handmade-descr">{t_descr}</table>' if t_descr else "")
        except:
            pass

        return ""

    def get_specs(self):
        specs = []

        fields1 = self.var_json.get('viewAttributes')
        if fields1:
            for k, v in fields1.items():
                if ('이벤트' in k) or ('사은품' in k):
                    continue
                specs.append({
                    "name": k,
                    "value": v
                })

        fields2 = self.var_json.get('detailAttributes')
        if fields2:
            for k, v in fields2.items():
                specs.append({
                    "name": k,
                    "value": v
                })

        return (specs if specs else None)

    def get_cats(self):
        cats_txt = self.basic_json.get('category')
        if not cats_txt:
            return None
        return " > ".join(cats_txt.split(">"))

    def get_images(self):
        img_list = self.var_json.get('productImages')
        if not img_list:
            return None
        return ";".join([img['url'] for img in img_list])

    def get_avail_qty(self, existence: bool):
        if not existence:
            return 0
        return self.var_json.get('stockQuantity')

    def get_opts_vars(self, price_krw: int):
        has_opts = self.var_json.get('optionUsable')
        if not has_opts:
            return (None, None)

        options = []
        variants = []

        opt_list = self.var_json.get('options')
        if opt_list:
            opt_combos = self.var_json.get('optionCombinations')
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
        recens = self.basic_json.get('aggregateRating')
        if not recens:
            return (None, None)
        return (recens['reviewCount'], recens['ratingValue'])

    def get_deliv_fee(self):
        deliv_info = self.var_json.get('productDeliveryInfo')
        if (not deliv_info) or (deliv_info['deliveryFeeType'].lower() == 'free'):
            return 0.00
        return round(deliv_info['baseFee']/self.krw_rate, 2)

    def get_deliv_days(self):
        try:
            deliv_txt = self.var_json['productInfoProvidedNoticeView']['additional']['주문 이후 예상되는 배송기간']

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

    async def get_prod_info(self, i: int, prod_id: str):
        url = 'https://shopping.naver.com/window-products/handmade/'+prod_id
        print(f'\n{i:_}/{len(self.todos):_}'.replace("_", "."), url)

        try:
            j = 1
            resp = await self.page.goto(url)
            while (resp.status >= 300) or ('internalerror' in resp.url):
                resp = await self.page.goto(url)
                if resp.status == 404:
                    print("Product not found")
                    return
                else:
                    print(f"Nav fail with status {resp.status}: {url} -> {resp.url} ({j}/3)")
                    j += 1
                    if j >= 3:
                        raise Exception(f'{url} -> {resp.url} (status {resp.status})')
                    await self.pause(300)
                    resp = await self.page.goto(url)

            await self.get_basic_json()
            await self.get_var_json()

            images = self.get_images()
            if not images:
                print("No images")
                return

            existence = self.get_exist()
            description = self.get_div_descr(prod_id)+self.get_table_descr()
            price_krw = self.basic_json.get('offers', {}).get('price', 0)
            options, variants = self.get_opts_vars(price_krw)
            reviews, rating = self.get_recensions()
            ship_dmin, ship_dmax = self.get_deliv_days()

            product = {
                "date": datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                "url": url,
                "source": "Naver",
                "product_id": prod_id,
                "existence": existence,
                "title": self.basic_json['name'],
                "title_en": None,
                "description": (description if description else None),
                "description_en": None,
                "summary": None,
                "sku": prod_id,
                "upc": prod_id,
                "brand": self.basic_json.get('description'),
                "specifications": self.get_specs(),
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
                "weight": None, # 有的商品参数中有两个不同的重量值
                "length": None,
                "width": None,
                "height": None
            }
            print(product)
            self.dones += 1
            self.count()
            return product
        except Exception as e:
            print("ERROR:", str(e))
            self.errs += 1
            self.count()
            await self.pause(280)
            return prod_id

    async def write_files(self):
        mode = 'a' if self.review else 'w'
        with open('naver_handmade_prods.txt', mode, encoding='utf-8') as f_prods, open('naver_handmade_prods_errs.txt', 'w', encoding='utf-8') as f_errs:
            async for y in self.scrape():
                if isinstance(y, dict):
                    json.dump(y, f_prods, ensure_ascii=False)
                    f_prods.write(',\n')
                elif isinstance(y, str): # 出错的商品号
                    f_errs.write(y+'\n')

        try:
            await self.browser.close()
        except:
            pass

        if self.errs:
            sys.exit(1)
        else:
            sys.exit(0)


async def main():
    review = False
    if (len(sys.argv) >= 2) and (sys.argv[1] == '--review'):
        review = True

    todos = []
    if not review:
        with open('naver_handmade_prods_ids.txt', 'r', encoding='utf-8') as prods_ids:
            for line in prods_ids:
                todos.append(line.strip())

    nc_recs = NaverHandmadeProduct(review, todos)
    await nc_recs.write_files()


if __name__ == '__main__':
    asyncio.run(main())
