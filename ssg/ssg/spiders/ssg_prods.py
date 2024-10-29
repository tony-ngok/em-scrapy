import json
import os
import re
from datetime import date, datetime

import requests
from bs4 import BeautifulSoup
import scrapy
from scrapy.http import HtmlResponse


# scrapy crawl ssg_prod
class SsgProds(scrapy.Spider):
    name = "ssg_prod"
    allowed_domains = ["www.ssg.com", "itemdesc.ssg.com", "department.ssg.com"]

    custom_settings = {
        'DOWNLOAD_DELAY': 0.1,
        'DOWNLOADER_MIDDLEWARES': { # 每发送请求后，先经过中间件返回回答，然后将回答通过回调函数处理
            'ssg.middlewares.SsgProdsErrsMiddleware': 543
        }
    }

    DESCR_IMG_FILTERS = ['%EB%B0%B0%EB%84%88', '/common/', '/top_banner', '/promotion',
                         '/brand', '/return', '/notice', '/ulfine', '/product/000000/', '/note',
                         '/delivery', '%EB%B0%B0%EC%86%A1', '%EB%B0%98%ED%92%88',
                         '%EC%95%88%EB%82%B4', '%EA%B5%90%ED%99%98', '%ED%83%9D%EB%B0%B0',
                         '%EC%BF%A0%ED%8F%B0', '/shipping', '%EA%B3%B5%EC%A7%80', '/gift',
                         '%EA%B8%B0%ED%94%84%ED%8A%B8', '%EC%A0%80%EC%9E%91%EA%B6%8C', '/copyright']
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

        self.krw_rate = 1383.172366
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
        sold_out = response.css("a.cdtl_btn_soldout, a.cdtl_btn_temp")
        return (('instock' in stock_txt) and (not sold_out))

    def get_existence_special(self, scr_txt: str):
        sold_out = re.findall(r"soldOut\s*:\s*'(Y|N)'", scr_txt)[0]
        if sold_out == 'Y':
            return False

        sold_out_pass = re.findall(r"soldOutPass\s*:\s*'(Y|N)'", scr_txt)[0]
        return (sold_out_pass == 'N')

    def get_descr(self, soup: str | BeautifulSoup):
        """
        使用BeautifulSoup整理描述
        """

        descr = ""
        if isinstance(soup, str):
            soup = BeautifulSoup(soup, 'html.parser')

        # 遍历所有子要素（包括纯文字）
        for child in soup.children:
            if child.name: # HTML要素
                if child.name == 'div':
                    descr += self.get_descr(child)
                elif child.name not in {'script', 'button', 'a', 'input', 'form', 'link'}:
                    child_str = str(child).strip()
                    if child_str:
                        filt = False
                        if '<img' in child_str:
                            for f in self.DESCR_IMG_FILTERS:
                                if f in child_str.lower(): # 过滤掉无用资料的图片
                                    filt = True
                                    break
                        if not filt:
                            descr += child_str
            elif isinstance(child, str): # 纯文字
                child_strip = child.strip()
                if child_strip:
                    txt_filt = False
                    for tf in self.DESCR_TXT_FILTERS: # 过滤掉版权信息等
                        if tf in child_strip.lower():
                            txt_filt = True
                            break
                    if not txt_filt:
                        descr += child_strip

        descr = " ".join(descr.split())
        return descr

    def get_specs_etc(self, response: HtmlResponse, selectors_th: str, selectors_td: str):
        """
        先提取参数，重量这些的稍后分别处理
        """

        specs = []
        table_descr = ""
        weight = None

        thx = response.css(selectors_th)
        tdx = response.css(selectors_td)

        weight_added = False
        for th, td in zip(thx, tdx):
            th_txt = th.css("::text").get("").strip()
            td_txt = td.css("::text").get("").strip()

            if th_txt and td_txt:
                if ('전화번호' in th_txt) or ('보증' in th_txt) or ('A/S' in th_txt) or ('반품' in th_txt) or ('인증' in th_txt):
                    continue
                if ('성분' in th_txt) or ('주의사항' in th_txt) or ('방법' in th_txt) or ('기한' in th_txt): # 值较长的参数（成分、注意事项、使用方法等）看作描述
                    table_descr += f'<tr><th>{th_txt}</th><td>{td_txt}</td></tr>'
                    continue
                if ('용량' in th_txt) and weight_added:
                    continue

                specs.append({
                    "name": th_txt,
                    "value": td_txt
                })
                if ('용량' in th_txt) or ('중량' in th_txt) or ('무게' in th_txt): # 重量参数不重复
                    weight = self.parse_weight(td_txt.lower())
                    weight_added = True

        return (specs if specs else None), (f'<table class="ssg-descr">{table_descr}</table>' if table_descr else ""), weight

    def parse_weight(self, txt: str):
        weight_match = re.findall(r'(\d+(?:\.\d+)?)\s*(g|ml|kg|l)', txt)
        if weight_match:
            if weight_match[1] in {'g', 'ml'}:
                return round(float(weight_match[0])/453.59237, 2)
            elif weight_match[1] in {'kg', 'l'}:
                return round(float(weight_match[0])*2.20462, 2)

    def get_categories(self, response: HtmlResponse):
        cats_dict = {}
        cats_sels = response.css('div.lo_depth_01 > a::text')[1:].getall()
        for c in cats_sels:
            if c and c.strip() and (c.strip() not in cats_dict):
                cats_dict[c.strip()] = True

        return " > ".join(cats_dict.keys()) if cats_dict else None

    def get_categories_special(self, scr_txt: str):
        cats_dict = {}
        cat_list = re.findall(r"stdCtg[L|M|S|D]clsNm\s*:\s*'(.*)'", scr_txt)
        for c in cat_list:
            if c and c.strip() and (c.strip() not in cats_dict):
                cats_dict[c.strip()] = True

        return " > ".join(cats_dict.keys()) if cats_dict else None

    def get_media(self, img_list: list[str], response: HtmlResponse):
        images = ";".join(["https://"+img for img in img_list])

        vid = response.css('input#vodDataFileNm::attr(value)').get()
        videos = "https://sc3po.ssgcdn.com"+vid+"_h.mp4?w=w" if vid else None

        return images, videos

    def get_vars_infos(self, resp_txt: str, opts_list: list[str], prod_id: str, exist: bool):
        """
        获得商品存货数量，以及所有变种资料
        """

        qty_match = re.findall(r"usablInvQty:'(\d+)'", resp_txt)
        available_qty = int(qty_match[0]) if exist else 0

        variants = []
        if opts_list:
            opts = len(opts_list)
            qty_match = qty_match[1:]
            uitemid_match = re.findall(r"uitemId:'(\d+)'", resp_txt)[1:]
            uitemoptnnm_match = re.findall(r"uitemOptnNm\d:'([^\']+)'", resp_txt)
            bestamt_match = re.findall(r"bestAmt:'(\d+)'", resp_txt)[1:]

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

    def get_recensions_special(self, response: HtmlResponse):
        reviews_sel = response.css('input#commentTotalCnt::attr(value)').get()
        rating_sel = response.css('span.cdtl_star_score > span.cdtl_txt::text').get()
        return (int(reviews_sel) if reviews_sel else None), (round(float(rating_sel.strip()), 2) if rating_sel else None)

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
        url = response.url.split('&')[0]
        if ('판매가 종료된' in response.text) or ('존재하지 않습니다' in response.text) or ('행사 기간이 아닙니다' in response.text):
            print(f"{i:_}/{len(self.start_urls):_}".replace("_", "."), "Item not found (ignored)")
            return
        if ('checkAdult.ssg' in url) or ('login.ssg' in url):
            print(f"{i:_}/{len(self.start_urls):_}".replace("_", "."), "Adult item (ignored)")
            return
        if ('dealItemView' in url):
            print(f"{i:_}/{len(self.start_urls):_}".replace("_", "."), "Promotion set (ignored)")
            return

        print(f"{i:_}/{len(self.start_urls):_}".replace("_", "."), url)

        special = False # 有些商品是百货店特别商品
        if '/special/' in url:
            special = True

        now = datetime.now()
        product_id = url.split("itemId=")[1]

        if special:
            data_obj = None
            for scr in response.css('script[type="text/javaScript"]'):
                scr_txt = scr.css("::text").get("").strip()
                if 'var resultItemObj' in scr_txt:
                    data_obj = scr
            if not data_obj:
                print(f"{i:_}/{len(self.start_urls):_}".replace("_", "."), "No product object")
                return

            im_list = response.css('ul.cdtl_pager_lst img::attr(src)').getall()
            if not im_list:
                print(f"{i:_}/{len(self.start_urls):_}".replace("_", "."), "No media")
                return
            images = ";".join([img.replace('_140', '') for img in im_list])

            existence = self.get_existence_special(scr_txt)
            title = re.findall(r"itemNm\s*:\s*'(.*)'", scr_txt)[0].strip()
            specifications, description, weight = self.get_specs_etc(response, 'div#item_detail_contents th', 'div#item_detail_contents td')
            brand = re.findall(r"brandNm\s*:\s*'(.*)'", scr_txt)[0] if re.findall(r"brandNm\s*:\s*'(.*)'", scr_txt) else None
            categories = self.get_categories_special(scr_txt)
            videos = None

            price_krw = float(re.findall(r"bestAmt\s*:\s*parseInt\('(\d+)'", scr_txt)[0])
            price = round(price_krw/self.krw_rate, 2)

            reviews, rating = self.get_recensions_special(response)
            shipping_fee = round(3000/self.krw_rate, 2) if price_krw < 30000 else 0.00
            shipping_days = None
        else:
            prod_json = response.css('script[type="application/ld+json"]::text').get()
            if not prod_json:
                print(f"{i:_}/{len(self.start_urls):_}".replace("_", "."), "No product object")
                return
            prod_json = json.loads(prod_json)

            images, videos = self.get_media(prod_json.get("image", []), response)
            if not (images or videos):
                print(f"{i:_}/{len(self.start_urls):_}".replace("_", "."), "No media")
                return

            existence = self.get_existence(prod_json["offers"]["availability"].lower(), response)
            title = prod_json["name"]
            specifications, description, weight = self.get_specs_etc(response, 'div#item_size > div.cdtl_option_info th, div#item_size > div.cdtl_sec th', 'div#item_size > div.cdtl_option_info td, div#item_size > div.cdtl_sec td')
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
        available_qty, variants = self.get_vars_infos(response.text, opts_list, product_id, existence)

        item = {
            "date": now.strftime('%Y-%m-%dT%H:%M:%S'),
            "url": url,
            "source": "SSG.COM",
            "product_id": product_id,
            "existence": existence,
            "title": title,
            "title_en": None,
            "description": description,
            "description_en": None,
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
            "shipping_days_max": shipping_days,
            "weight": weight,
            "length": None,
            "width": None,
            "height": None
        }

        iframe_url = response.css('iframe#_ifr_html::attr(src)').get()
        if iframe_url:
            headers = { **self.HEADERS, 'referer': url }
            yield scrapy.Request(iframe_url, headers=headers,
                                 meta={ "cookiejar": response.meta["cookiejar"] },
                                 callback=self.parse_descr,
                                 cb_kwargs={ "item": item, "i": i })
        else:
            self.write_item(i, item)

    def parse_descr(self, response: HtmlResponse, i: int, item: dict):
        """
        先提取描述URL，然后之后再分别整理
        """

        if response.status != 404:
            descr_table = item["description"]
            descr = ""

            divx = response.css('body > div')
            for div in divx:
                if div.css('*'):
                    descr_raw = " ".join(div.get().split())
                    descr += self.get_descr(descr_raw)

            descr = f'<div class="ssg-descr">{descr}</div>' if descr else ""
            item['description'] = descr+descr_table if descr or descr_table else None

        self.write_item(i, item)

    def write_item(self, i: int, item: dict):
        print(f"{i:_}/{len(self.start_urls):_}".replace("_", "."), "success")

        mode = 'a' if self.retry else 'w'
        with open(self.output_file, mode, encoding='utf-8') as f_out:
            json.dump(item, f_out, ensure_ascii=False)
            f_out.write(",\n")
        if not self.retry:
            self.retry = True
