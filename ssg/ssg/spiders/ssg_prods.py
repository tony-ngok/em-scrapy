import json
import os
import re
from datetime import date, datetime

import requests
import scrapy
from scrapy.http import HtmlResponse

# scrapy crawl ssg_prod
class SsgProds(scrapy.Spider):
    name = "ssg_prod"
    allowed_domains = ["www.ssg.com", "itemdesc.ssg.com"]

    custom_settings = {
        'DOWNLOAD_DELAY': 0.1,
        'DOWNLOADER_MIDDLEWARES': { # 每发送请求后，先经过中间件返回回答，然后将回答通过回调函数处理
            'ssg.middlewares.SsgProdsErrsMiddleware': 543
        }
    }

    DESCR_IMG_FILTERS = [
        '배너', '%EB%B0%B0%EB%84%88', '/common/', '/top_banner', '/promotion',
        '/brand', '/return', '/notice', '/ulfine'
        ]
    DESCR_TXT_FILTERS = ['ssg.com', '저작권', 'copyright']

    HEADERS = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "de-DE,de;q=0.9,en-GB;q=0.8,en;q=0.7",
        "connection": "keep-alive",
        "dnt": "1",
        "referer": "",
        "sec-ch-ua": '"Chromium";v="130", "Microsoft Edge";v="130", "Not?A_Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0"
    }

    CM_TO_IN = 0.393701
    G_TO_LB = 0.002205
    KG_TO_LB = 2.20462
    M_TO_IN = 39.37008

    def __init__(self, start_urls: list[str] = [], retry: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = start_urls
        self.retry = retry
        self.output_file = "ssg_products.txt"

        if not self.retry:
            print("Start anew")
            pids_file = "ssg_prods_ids.txt"
            if os.path.exists(pids_file):
                with open(pids_file, 'r', encoding="utf-8") as f_ids:
                    for line in f_ids:
                        if line.strip():
                            self.start_urls.append(line.strip())
            else:
                print("Pids file not found:", pids_file)
        else:
            print("Retry mode")

        self.krw_rate = 1379.40808
        rate_req = requests.get('https://open.er-api.com/v6/latest/USD')
        if rate_req.ok:
            self.krw_rate = rate_req.json()['rates']['KRW']
            print(f"Latest USD/KRW rate: {self.krw_rate:_}".replace(".", ",").replace("_", "."))
        else:
            print(f"Fail to get latest USD/KRW rate (default: {self.krw_rate:_})".replace(".", ",").replace("_", "."))

    def start_requests(self):
        for i, url in enumerate(self.start_urls):
            url = "https://www.ssg.com/item/itemView.ssg?itemId="+url
            yield scrapy.Request(url, headers=self.HEADERS,
                                 meta={ "cookiejar": i },
                                 callback=self.parse,
                                 cb_kwargs={ "i": i+1 })

    def get_existence(self, stock_txt: str, response: HtmlResponse):
        sold_out = response.css("a.cdtl_btn_soldout")
        return (('instock' in stock_txt) and (not sold_out))

    def get_specs_etc(self, response: HtmlResponse):
        """
        先提取参数，重量这些的稍后分别处理
        """

        specs = []
        table_descr = ""

        thx = response.css('div[id="item_size"] > div.cdtl_option_info th, div[id="item_size"] > div.cdtl_sec th')
        tdx = response.css('div[id="item_size"] > div.cdtl_option_info td, div[id="item_size"] > div.cdtl_sec td')

        for th, td in zip(thx, tdx):
            th_txt = th.css("::text").get("").strip()
            td_txt = td.css("::text").get("").strip()

            weight_added = False
            if th_txt and td_txt:
                if ('전화번호' in th_txt) or ('보증' in th_txt) or ('A/S' in th_txt) or ('반품' in th_txt) or ('인증' in th_txt):
                    continue
                if ('성분' in th_txt) or ('주의사항' in th_txt) or ('방법' in th_txt) or ('기한' in th_txt):
                    table_descr += f'<tr><th>{th_txt}</th><td>{td_txt}</td></tr>'
                if ('용량' in th_txt) and weight_added:
                    continue

                specs.append({
                    "name": th_txt,
                    "value": td_txt
                })
                if ('용량' in th_txt) or ('중량' in th_txt): # 重量参数不重复
                    weight_added = True

        return (specs if specs else None), (f'<table class="ssg-descr">{table_descr}</table>' if table_descr else "")

    def get_categories(self, response: HtmlResponse):
        cats_dict = {}
        cats_sels = response.css('div.lo_depth_01 > a::text')[1:].getall()
        for c in cats_sels:
            if c and c.strip() and (c.strip() not in cats_dict):
                cats_dict[c] = True

        return " > ".join(cats_dict.keys()) if cats_dict else None

    def get_media(self, img_list: list[str], response: HtmlResponse):
        images = ";".join(["https://"+img for img in img_list])

        vid = response.css('input#vodDataFileNm::attr(value)').get()
        videos = "https://sc3po.ssgcdn.com"+vid+"_h.mp4?w=w" if vid else None

        return images, videos

    def get_vars_infos(self, resp_txt: str, opts_list: list[str], prod_id: str):
        """
        获得商品存货数量，以及所有变种资料
        """

        qty_match = re.findall(r"usablInvQty:'(\d+)'", resp_txt)
        available_qty = int(qty_match[0])

        variants = []
        if opts_list:
            opts = len(opts_list)
            qty_match = qty_match[1:]
            uitemid_match = re.findall(r"uitemId:'(\d+)'", resp_txt)[1:]
            uitemoptnnm_match = re.findall(r"uitemOptnNm\d:'([^\']+)'", resp_txt)
            bestamt_match = re.findall(r"bestAmt:'(\d+)'")[1:]

            for j, (qty, uitemid, bestamt) in enumerate(zip(qty_match, uitemid_match, bestamt_match)):
                variants.append({
                    "variant_id": f"{prod_id}-{uitemid}",
                    "barcode": None,
                    "sku": f"{prod_id}-{uitemid}",
                    "option_values": [{
                        "option_id": None,
                        "option_value_id": None,
                        "option_name": opt,
                        "option_value": uitemoptnnm
                    } for opt, uitemoptnnm in zip(opts_list, uitemoptnnm_match[j*opts:(j+1)*opts])],
                    "images": None,
                    "price": round(float(bestamt)/self.krw_rate, 2),
                    "available_qty": int(qty)
                })

        return available_qty, (variants if variants else None)

    def get_recensions(self, recensions: dict):
        if not recensions:
            return None, None
        return int(recensions["reviewCount"]), round(float(recensions["ratingValue"]), 2)

    def get_deliv_fee(self, response: HtmlResponse):
        deliv_fee = response.css('dl.cdtl_delivery_fee em.ssg_price::text').get()
        if not deliv_fee:
            return 0.00
        return round(float(deliv_fee.replace(",", ""))/self.krw_rate, 2)

    def get_ship_days(self, response: HtmlResponse, toyear: int, tomonth: int, today: int):
        deliv_days_info = response.css('li[name="delivery_info"] p.info_detail_txt::text').get()
        if not deliv_days_info:
            return None
        if '내일' in deliv_days_info:
            return 1

        date_match = re.findall(r"(\d+)/(\d+)", deliv_days_info)
        if date_match:
            deliv_month, deliv_day = date_match[0]
            deliv_month = int(deliv_month)
            deliv_day = int(deliv_day)

            if deliv_month < tomonth:
                deliv_date = date(toyear+1, deliv_month, deliv_day)
            else:
                deliv_date = date(toyear, deliv_month, deliv_day)
            return (deliv_date-date(toyear, tomonth, today)).days

    def parse(self, response: HtmlResponse, i: int):
        url = response.request.url.split('&')[0]
        print(f"\n{i:_}/{len(self.start_urls):_}".replace("_", "."), url)

        now = datetime.now()
        product_id = url.split("itemId=")[1]

        prod_json = response.css('script[type="application/ld+json"]::text').get()
        if not prod_json:
            print("No product JSON")
            return
        prod_json = json.loads(prod_json)

        images, videos = self.get_media(prod_json.get("image", []), response)
        if not (images or videos):
            print("No media")
            return

        existence = self.get_existence(prod_json["offers"]["availability"].lower(), response)
        title = prod_json["name"]
        description, specifications = self.get_specs_etc(response)
        brand = prod_json["brand"]["name"]
        categories = self.get_categories(response)
        price = round(float(prod_json["offers"]["price"])/self.krw_rate, 2)
        reviews, rating = self.get_recensions(prod_json.get("aggregateRating", {}))
        shipping_fee = self.get_deliv_fee(response)
        shipping_days = self.get_ship_days(response, now.year, now.month, now.day)

        opts_list = response.css('dl.cdtl_opt_group > dt::text').getall()
        options = [{
            "id": None,
            "name": opt
        } for opt in opts_list] if opts_list else None
        available_qty, variants = self.get_vars_infos(response.text, opts_list, product_id)

        item = {
            "date": now.strftime('%Y-%m-%dT%H:%M:%S'),
            "url": url,
            "source": "SSG.COM",
            "product_id": product_id,
            "existence": existence,
            "title": title,
            "title_en": None,
            "description": description, # 暂时先只存放表格描述
            "description_en": "", # 存放iframe描述的临时空间
            "summary": None,
            "sku": product_id,
            "upc": None,
            "brand": brand,
            "specifications": specifications,
            "categories": categories,
            "images": images,
            "videos": videos,
            "price": price,
            "available_qty": available_qty,
            "options": options,
            "variants": variants,
            "has_only_default_variant": not (variants and (len(variants) > 1)),
            "returnable": False,
            "reviews": reviews,
            "rating": rating,
            "sold_count": None,
            "shipping_fee": shipping_fee,
            "shipping_days_min": shipping_days,
            "shipping_days_max": shipping_days
        }

        iframe_url = response.css('iframe#_ifr_html::attr(src)').get()
        if iframe_url:
            headers = { **self.HEADERS, 'referer': url }
            yield scrapy.Request(iframe_url, headers=headers,
                                 meta={ "cookiejar": response.meta["cookiejar"] },
                                 callback=self.parse_descr,
                                 cb_kwargs={ "item": item })
        else:
            self.write_item(item)

    def parse_descr(self, response: HtmlResponse, item: dict):
        """
        先提取描述URL，然后之后再分别整理
        """

        if response.status != 404:
            divx = response.css('body > div')
            for div in divx:
                if div.css('*'):
                    item['description_en'] += div.get()

        self.write_item(item)

    def write_item(self, item: dict):
        print(item)

        mode = 'a' if self.retry else 'w'
        with open(self.output_file, mode, encoding='utf-8') as f_out:
            json.dump(item, f_out)
            f_out.write(",\n")
        if not self.retry:
            self.retry = True
