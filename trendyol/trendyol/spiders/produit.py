import asyncio
import json
import re
from datetime import datetime

import requests
import scrapy
from scrapy.http import HtmlResponse
from scrapy_playwright.page import PageMethod


# scrapy crawl trendyol_produit -O trendyol_produits.json # 复写整个数据
class TrendyolProduit(scrapy.Spider):
    name = 'trendyol_produit'
    allowed_domains = ['www.trendyol.com', 'apigw.trendyol.com']
    start_urls = [
        'https://www.trendyol.com/bubito/kislik-tatli-kapsonlu-bebek-pelus-welsoft-tulum-p-446949530',
        'https://www.trendyol.com/sihhat-pharma/sihhat-aqua-beyaz-vazelin-50-ml-p-51920806',
        'https://www.trendyol.com/the-fine-organics/avustralya-nanesi-aktif-karbon-dis-beyazlatma-tozu-50g-p-762586955',
        'https://www.trendyol.com/l-oreal-paris/panorama-hacim-veren-maskara-koyu-kahverengi-p-796043319',
        'https://www.trendyol.com/oxvin/walker-baggy-bol-paca-2-iplik-orta-kalinlikta-uzun-esofman-alti-orijinal-kalip-p-855410433',
        'https://www.trendyol.com/oxvin/walker-baggy-bol-paca-2-iplik-orta-kalinlikta-uzun-esofman-alti-orijinal-kalip-p-855410436',
        'https://www.trendyol.com/mert-sert-mobilya/vern-120cm-konsol-tv-sehpasi-tv-unitesi-kahve-kosesi-banyo-dolabi-cok-amacli-dolap-p-773280008',
        'https://www.trendyol.com/bioderma/sebium-foaming-gel-karma-yagli-ve-akne-egilimli-ciltler-icin-yuz-temizleme-jeli-500-ml-p-132469',
        'https://www.trendyol.com/copierbond/ve-ge-a4-fotokopi-kagidi-80-g-500-lu-5-paket-2500ad-1-koli-p-6026206'
    ]

    CM_TO_IN = 0.393701
    G_TO_LB = 0.002205
    KG_TO_LB = 2.20462
    M_TO_IN = 39.37008

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
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
            self.exch_rate = 34.234075
        finally:
            print(f"USD/TRY: {self.exch_rate}".replace('.', ','))
        
    def start_requests(self):
        for i, url in enumerate(self.start_urls, start=1):
            print(url, f"({i:_}/{len(self.start_urls):_})".replace("_", "."))

            id_match = re.findall(r'p-(\d+)$', url)
            if id_match:
                product_id = id_match[0]
                yield scrapy.Request(f'https://apigw.trendyol.com/discovery-web-productgw-service/api/product-detail/{product_id}/html-content?channelId=1',
                                     headers=self.headers,
                                     meta={
                                         "url": url,
                                         "product_id": product_id,
                                     },
                                     callback=self.pre_parse)

    def pre_parse(self, response: HtmlResponse):
        url = response.meta['url']
        product_id = response.meta['product_id']

        try:
            resp_json = response.json()
            descr_page = resp_json['result'] if resp_json['result'] else ''
            yield scrapy.Request(url, headers=self.headers,
                                 meta={
                                        "url": url,
                                        "product_id": product_id,
                                        "descr_page": descr_page,
                                        "playwright": True,
                                        "playwright_include_page": True,
                                        "playwright_page_methods": [
                                            PageMethod("wait_for_selector", "div.product-detail-wrapper")
                                        ]
                                     },
                                     callback=self.parse)
        except Exception as e:
            print("Preparse error:", url, f"({str(e)})")

    async def get_json(self, page):
        scr_appl = await page.query_selector_all('script[type="application/javascript"]')

        prod_json = None
        wp_json = None
        for scr in scr_appl:
            scr_txt = (await scr.text_content()).strip()

            json_match = re.findall(r'__PRODUCT_DETAIL_APP_INITIAL_STATE__=(\{.*\});', scr_txt)
            if json_match:
                prod_json = json.loads(json_match[0])['product']
            elif 'WebPage' in scr_txt:
                wp_json = json.loads(scr_txt)['breadcrumb']
            
            if prod_json and wp_json:
                break
        
        return (prod_json, wp_json)

    async def get_video(self, page):
        video = None

        video_sel = await page.query_selector('div.video-player')
        if video_sel:
            video_wait1 = await asyncio.gather(
                video_sel.click(),
                page.wait_for_selector('div.gallery-video-container')
            )

            video_wait2 = await asyncio.gather(
                video_wait1[1].click(),
                page.wait_for_selector('video.video-player > source[type="video/mp4"]', state='attached') # 不用等到要素出现在视窗中
            )

            video = await video_wait2[1].get_attribute('src')
        
        return video

    def parse_descr_info(self, descr_info: list):
        if not descr_info:
            return None

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
        if not specs_infos:
            return None
        
        specs = []
        weight = None
        length = None
        width = None
        height = None
        for spec in specs_infos:
            k = spec['key']['name']
            v = spec['value']['name']
            specs.append[{
                "name": k,
                "value": v
            }]

            kk = k.lower()
            vv = v.lower()
            if ('gramaj' in kk) or ('hacim' in kk) or ('ağırlık' in kk):
                weight = self.get_dim(vv, r'\b(\d+(?:\.\d+)?)\s?(g|kg|ml|l|cc)\b')
            elif ('derinlik' in kk):
                length = self.get_dim(vv, r'\b(\d+(?:\.\d+)?)\s?(m|cm)\b')
            elif ('genişlik' in kk):
                width = self.get_dim(vv, r'\b(\d+(?:\.\d+)?)\s?(m|cm)\b')
            elif ('yükseklik' in kk):
                height = self.get_dim(vv, r'\b(\d+(?:\.\d+)?)\s?(m|cm)\b')
        
        return {
            "specifications": specs,
            "weight": weight,
            "length": length,
            "width": width,
            "height": height
        }
    
    def parse_cats(self, cats_infos: list):
        if not cats_infos:
            return None
        
        return " > ".join([cat['name'] for cat in cats_infos])

    def parse_vars(self, opt_info: list, vars_infos: list):
        if not (opt_info and vars_infos):
            return None

        return [{
            "variant_id": str(vi['itemNumber']),
            "barcode": vi['barcode'],
            "sku": None,
            "option_values": [{
                "option_id": opt_info[0]['id'],
                "option_value_id": None,
                "option_name": opt_info[0]['name'],
                "option_value": vi['value']
            }],
            "images": None,
            "price": round(vi['price']/self.exch_rate, 2),
            "available_qty": 0 if not vi['inStock'] else None
        } for vi in vars_infos]

    def get_dim(self, txt: str, regex: str):
        dim_match = re.findall(regex, txt)
        if dim_match and len(dim_match) >= 2:
            val = float(dim_match[0])
            unit = dim_match[1]

            if unit in {'kg', 'l'}:
                return float(val*self.KG_TO_LB, 2)
            if unit in {'g', 'ml', 'cc', 'gr'}:
                return float(val*self.G_TO_LB, 2)
            if unit == 'm':
                return float(val*self.M_TO_IN, 2)
            if unit == 'cm':
                return float(val*self.CM_TO_IN, 2)

    async def parse(self, response: HtmlResponse):
        url = response.meta['url']
        product_id = response.meta['product_id']
        descr_page = response.meta['descr_page'].strip().replace('\n', '')
        page = response.meta['playwright_page']

        try:
            # 首次进入页面时
            accept = await page.query_selector('button#onetrust-accept-btn-handler')
            if accept:
                await asyncio.gather(
                    accept.click(),
                    page.reload()
                )
            init_butt = await page.query_selector('button.onboarding-popover__default-renderer-primary-button')
            if init_butt:
                await init_butt.click()
                await asyncio.sleep(1)
            
            prod_json, wp_json = await self.get_json(page)
            if not prod_json:
                raise Exception("No product JSON")
            if not wp_json:
                wp_json = {}

            img_list = prod_json.get('images')
            if not img_list:
                raise Exception("No images")
            
            price_raw = prod_json.get('price', {}).get('sellingPrice', {}).get('value')
            if price_raw is None:
                raise Exception("No price")
            price = round(price_raw/self.exch_rate, 2)

            descr_info = self.parse_descr_info(prod_json.get('descriptions', []))
            description = descr_info+descr_page if (descr_info or descr_page) else None

            existence = prod_json['hasStock'] and prod_json['isSellable']
            
            var_info = prod_json.get('variants')
            var_parse = self.parse_var_info(var_info if var_info else [{}])

            brand_info = prod_json.get('brand', {})
            brand = brand_info['name'] if brand_info.get('name') else None

            spec_info = self.parse_specs(prod_json.get('attributes', []))

            cats_list = wp_json.get('itemListElement', [])[1:-1]
            categories = " > ".join([cat['item']['name'] for cat in cats_list]) if cats_list else None

            video = await self.get_video(page)

            options = var_parse['options'] # 单一选项名
            variants = self.parse_vars(options, prod_json.get('allVariants'))
            
            recension = prod_json.get('ratingScore', {})
            reviews = recension.get('totalRatingCount')
            rating = recension.get('averageRating')

            yield {
                "date": datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                "url": url,
                "source": "Trendyol",
                "product_id": product_id,
                "existence": existence,
                "title": prod_json['name'],
                "title_en": None,
                "description": description,
                "description_en": None,
                "summary": None,
                "sku": product_id,
                "upc": var_parse['upc'],
                "brand": brand,
                "specifications": spec_info['specifications'],
                "categories": categories,
                "images": ";".join(["https://cdn.dsmcdn.com/"+img for img in img_list]),
                "videos": video,
                "price": price,
                "available_qty": var_parse['available_qty'] if existence else 0,
                "options": options,
                "variants": variants,
                "has_only_default_variant": not (variants and len(variants) > 1),
                "returnable": False,
                "reviews": reviews,
                "rating": rating,
                "sold_count": None,
                "shipping_fee": 0.00 if prod_json['isFreeCargo'] else round(34.99/self.exch_rate, 2), # https://www.trendyol.com/yardim/sorular/2002?grup=1
                "shipping_days_min": None,
                "shipping_days_max": None,
                "weight": spec_info['weight'],
                "length": spec_info['length'],
                "width": spec_info['width'],
                "height": spec_info['height']
            }
        except Exception as e:
            print("Parse error:", url, f"({str(e)})")
        finally:
            await page.close()
