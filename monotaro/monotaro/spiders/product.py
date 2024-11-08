# 使用上级目录中的utils
import sys
sys.path.append('..')

from datetime import datetime
from json import load, loads
from re import findall

import requests
from bs4 import BeautifulSoup, Tag
import scrapy
from scrapy.http import HtmlResponse


# scrapy crawl monotaro_product
class MonotaroProduct(scrapy.Spider):
    name = "monotaro_product"
    allowed_domains = ["www.monotaro.com"]
    start_urls = []

    CM_TO_IN = 0.393701
    M_TO_IN = 39.37008
    MM_TO_IN = 0.0393701
    G_TO_LB = 0.002205
    KG_TO_LB = 2.20462

    HEADERS = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
        "Accept-Language": "pt-PT,pt;q=0.8,en-GB;q=0.5,en;q=0.3",
        "Referer": "https://www.google.pt",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0"
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        with open('monotaro_prod_urls.json', 'r') as f:
            produits = load(f)
        self.start_urls = [p['prod_url'] for p in produits]
        print(f'Total {len(self.start_urls):_} products'.replace("_", "."))

        self.jpy_rate = 153.237093
        try:
            resp = requests.get('https://open.er-api.com/v6/latest/USD')
            if resp.ok:
                self.jpy_rate = resp.json()['rates']['JPY']
            else:
                raise Exception(f'Status {resp.status_code}')
        except Exception as e:
            print("Fail to get latest USD/JPY rate", str(e))
        finally:
            print(f"USD/JPY rate: {self.jpy_rate:_}".replace(".", ",").replace("_", "."))

    def get_prod_url(self, prod_id: str, p: int = 1):
        if p > 1:
            return f'https://www.monotaro.com/g/{prod_id}/page-{p}/'
        return f'https://www.monotaro.com/g/{prod_id}/'

    def get_basic_descr(self, response):
        basic_descr = ""

        if isinstance(response, HtmlResponse):
            response = BeautifulSoup(response.css('p.DescriptionText').get(''), 'html.parser')
            response = response.p
            if not response:
                return ""

        for child in response.children:
            if isinstance(child, str):
                basic_descr += " ".join(child.strip().split())
            elif isinstance(child, Tag):
                if child.name == 'a':
                    return ""
                elif child.name == 'br':
                    basic_descr += '<br>'
                else:
                    basic_descr += self.get_basic_descr(child)

        return basic_descr

    def get_alert_descr(self, response):
        alert_descr = ""

        if isinstance(response, HtmlResponse):
            response = BeautifulSoup(response.css('div.product_data_caution').get(''), 'html.parser')
            response = response.div
            if not response:
                return ""

        for child in response.children:
            if isinstance(child, str):
                alert_descr += " ".join(child.strip().split())
            elif isinstance(child, Tag):
                if child.name == 'a':
                    return ""
                elif (child.name == 'div') and ('product_data_caution-title' in child.get('class')):
                    alert_descr += '<h4>注意</h4>'
                elif child.name == 'br':
                    alert_descr += '<br>'
                else:
                    alert_descr += self.get_basic_descr(child)

        return alert_descr

    def get_specs_etc(self, response: HtmlResponse):
        specs = []
        add_descr = ""

        spans = response.css('span.AttributeLabel__Wrap').getall()
        for span in spans:
            if span:
                span = BeautifulSoup(span, 'html_parser')
                span = span.span

                spec_name = ''
                spec_val = ''
                is_add_descr = False

                for child in span.children:
                    if isinstance(child, Tag) and (child.name == 'span'):
                        spec_name = child.text.strip()
                    elif isinstance(child, Tag) and (child.name == 'div'): # 较长的参数值放入描述中
                        is_add_descr = True
                        spec_val = " ".join(child.text.strip().replace("\n", '<br>').split())
                    elif isinstance(child, str):
                        if "。" in spec_val:
                            is_add_descr = True
                        spec_val = child.text.strip()

                if spec_name and spec_val:
                    if is_add_descr:
                        add_descr += f'<tr><th>{spec_name}</th><td>{spec_val}</td></tr>'
                    else:
                        specs.append({
                            "name": spec_name,
                            "value": spec_val
                        })

        return (specs if specs else None), add_descr

    def combine_descr(self, basic_descr: str, add_descr: str, alert_descr: str):
        descr1 = f'<div class="monotaro-descr">{basic_descr}</div>' if basic_descr else ""
        descr2 = f'<table class="monotaro-descr">{add_descr}</table>' if add_descr else ""
        descr3 = f'<div class="monotaro-descr">{alert_descr}</div>' if alert_descr else ""
        return descr1+descr2+descr3 if descr1 or descr2 or descr3 else None

    def get_brand(self, dat: dict):
        if dat.get('brand'):
            return dat['brand'].get('name') or None

    def get_cats(self, cat_dat: dict):
        cat_list = [item['item']['name'] for item in cat_dat.get('itemListElement', [])[1:]]
        if cat_list:
            return " > ".join(cat_list)
        return None

    def get_images(self, response: HtmlResponse):
        imgx = response.css('img.ProductImage--Lg::attr(src)').getall()
        img_list = ['https:'+img for img in imgx if img and 'mono_image_na' not in img]
        return ";".join(img_list)

    def get_videos(self, response: HtmlResponse):
        vidx = response.css('a.ytp-title-link::attr(href)').getall()
        vid_list = [vid for vid in vidx if vid]
        return ";".join(vid_list)

    def get_recensions(self, dat: dict):
        recens = dat.get('aggregateRating')
        if recens:
            return recens['ratingCount'], round(float(recens['ratingValue']), 2)
        return None, None

    def start_requests(self):
        for i, pid in enumerate(self.start_urls):
            url = self.get_prod_url(pid)
            yield scrapy.Request(url, headers=self.HEADERS,
                                 meta={ 'cookiejar': i },
                                 callback=self.parse,
                                 cb_kwargs={ 'i': i+1, "pid": pid })

    def parse(self, response: HtmlResponse, i: int, pid: str, p: int = 1, item: dict = {}):
        print(f"{i:_}/{len(self.start_urls):_}", response.url)

        if p == 1: # 提取商品资料
            if response.status == 404:
                print("Product not found", response.url)
                return

            prod_json = None
            bc_json = None
            for scr in response.css('script[type="application/ld+json"]::text').getall():
                if '"Product"' in scr:
                    prod_json = loads(scr)
                elif 'BreadCrumbList"' in scr:
                    bc_json = loads(scr)
                if prod_json and bc_json:
                    break
            if not (prod_json and bc_json):
                print("No product info", response.url)
                return

            item['title'] = prod_json.get('name')
            if not item['title']:
                print("No name", response.url)
                return

            item['images'] = self.get_images(response)
            if not item['images']:
                print("No images", response.url)
                return

            item['url'] = response.url
            item['source'] = 'MonotaRO'
            item['product_id'] = pid

            item['specifications'], add_descr = self.get_specs_etc(response)
            basic_descr = self.get_basic_descr(response)
            alert_descr = self.get_alert_descr(response)
            item['description'] = self.combine_descr(basic_descr, add_descr, alert_descr)

            item['description_en'] = None
            item['summary'] = None
            item['upc'] = None
            item['brand'] = self.get_brand(prod_json)
            item['categories'] = self.get_cats(bc_json)
            item['videos'] = self.get_videos(response)
            item['returnable'] = False
            item['reviews'], item['rating'] = self.get_recensions(prod_json)
            item['sold_count'] = None

            # https://help.monotaro.com/app/answers/detail/a_id/13
            item['shipping_days_min'] = 1
            item['shipping_days_max'] = 10
        else: # 变种超过50个：继续提取变种
            pass

        more_vars = response.css('a.Button--PaginationNext')
        if more_vars:
            next_purl = self.get_prod_url(pid, p+1)
            headers = { **self.HEADERS, 'Referer': response.url }
            yield scrapy.Request(next_purl, headers=headers,
                                 meta={ 'cookiejar': response.meta['cookiejar'] },
                                 callback=self.parse,
                                 cb_kwargs={ 'i': i+1, "pid": pid, "p": p+1, "item": item })
        else:
            item['variants'] = item['variants'] if item['variants'] else None
            yield item
