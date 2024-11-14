# 使用上级目录中的utils
import sys
sys.path.append('..')

import json
import re
from datetime import datetime

# import requests
from bs4 import BeautifulSoup, Tag
import scrapy
from scrapy.http import HtmlResponse
from scrapy.selector import SelectorList


# scrapy crawl trendyol_produit
class TrendyolProduit(scrapy.Spider):
    name = 'trendyol_produit'
    allowed_domains = ['www.trendyol.com', 'apigw.trendyol.com']
    start_urls = []

    # custom_settings = {
    #     "ITEM_PIPELINES": {
    #         "trendyol.pipelines.MongoPipeLine3": 400,
    #     }
    # }

    COOKIES = {
        "FirstSession": "0",
        "ForceUpdateSearchAbDecider": "forced",
        "OptanonAlertBoxClosed": "2024-11-11T16:04:45.521Z",
        "OptanonConsent": "isGpcEnabled=0&datestamp=Mon+Nov+11+2024+10%3A04%3A50+GMT-0600+(hora+est%C3%A1ndar+central)&version=6.30.0&isIABGlobal=false&hosts=&genVendors=V77%3A0%2CV67%3A0%2CV79%3A0%2CV71%3A0%2CV69%3A0%2CV7%3A0%2CV5%3A0%2CV9%3A0%2CV1%3A0%2CV70%3A0%2CV3%3A0%2CV68%3A0%2CV78%3A0%2CV17%3A0%2CV76%3A0%2CV80%3A0%2CV16%3A0%2CV72%3A0%2CV10%3A0%2CV40%3A0%2C&consentId=bb0f89e6-3e05-476e-bea1-f2a2e4d4ab88&interactionCount=1&landingPath=NotLandingPage&groups=C0002%3A1%2CC0004%3A1%2CC0003%3A1%2CC0001%3A1%2CC0007%3A1%2CC0009%3A1&geolocation=TR%3B06&AwaitingReconsent=false",
        "SearchMode": "1",
        "VisitCount": "1",
        "WebAbTesting": "A_14-B_46-C_100-D_15-E_93-F_27-G_21-H_13-I_85-J_97-K_55-L_85-M_49-N_16-O_80-P_96-Q_12-R_43-S_70-T_100-U_85-V_47-W_71-X_49-Y_71-Z_45",
        "WebRecoAbDecider": "ABcrossRecoVersion_1-ABcrossRecoAdsVersion_1-ABsimilarRecoAdsVersion_1-ABsimilarSameBrandVersion_1-ABattributeRecoVersion_1-ABbasketRecoVersion_1-ABcollectionRecoVersion_1-ABshopTheLookVersion_1-ABcrossSameBrandVersion_1-ABcompleteTheLookVersion_1-ABsimilarRecoVersion_1-ABpdpGatewayVersion_1-ABhomepageVersion_firstComponent%3AinitialNewTest_1.performanceSorting%3AwidgetPerformanceFreqV1_3.sorter%3AhomepageSorterNewTest_d%28M%29-ABnavigationSideMenuVersion_sideMenu%3AinitialTest_1%28M%29-ABnavigationSectionVersion_section%3AazSectionTest_1%28M%29",
        "__cf_bm": "phfrOpULWrqS.QC1d0PEvPmXBBI7AClvBkKJDTmQTfs-1731341078-1.0.1.1-8GVC3XMsmmGdi0oLj.bx9RMKQRnvtC4vGvNExTf_Ev0YqKCr9y.92co24deWkcEpXO7Pd3cI6IBl8.xhptgmCw",
        "_cfuvid": "vnnSDSct1UUsdrnhOJ3rEs24JjGNGPondl95HNInMH4-1731341078622-0.0.1.1-604800000",
        "_fbp": "fb.1.1731341089980.416062928773427444",
        "_gcl_au": "1.1.81461011.1731341088",
        "_ym_d": "1731341092",
        "_ym_isad": "2",
        "_ym_uid": "1731341092939299798",
        "hvtb": "1",
        "msearchAb": "ABSearchFETestV1_A-ABSuggestionLC_B-ABSuggestionPS_A",
        "pid": "5150f76a-af49-4b83-9795-9a47243bdfae",
        "platform": "web",
        "recoAb": "ABRecoBETestV1_B-ABRecoFirstTest_A",
        "sid": "Ux7FkHQJOe"
    }

    HEADERS = {
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

    CM_TO_IN = 0.393701
    G_TO_LB = 0.002205
    KG_TO_LB = 2.20462
    M_TO_IN = 39.37008

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # with open('trendyol_prods_urls.txt', 'r', encoding='utf-8') as f_in:
        #     for line in f_in:
        #         if line.strip():
        #             self.start_urls.append(line.strip())
        # print(f"Total {len(self.start_urls):_} produit(s)".replace('_', '.'))

        self.exch_rate = 34.377928
        # exch = requests.get('https://open.er-api.com/v6/latest/USD')
        # try:
        #     if exch.status_code in range(200, 300):
        #         exch_data = exch.json()
        #         self.exch_rate = exch_data['rates']['TRY']
        #         print("Get USD/TRY")
        #     else:
        #         raise Exception("Get USD/TRY: error", exch.status_code)
        # except Exception as e:
        #     print(str(e))
        # finally:
        #     print(f"USD/TRY: {self.exch_rate}".replace('.', ','))

    def start_requests(self):
        for i, todo in enumerate(self.start_urls):
            url = 'https://www.trendyol.com/'+todo
            yield scrapy.Request(url, headers=self.HEADERS,
                                 meta={ "cookiejar": i },
                                 callback=self.parse)

    def get_json(self, response: HtmlResponse):
        '''
        获得重要数据聚集的JSON
        '''

        scrs = response.css('script[type="application/javascript"]')

        prod_json = None
        for scr in scrs:
            scr_txt = scr.css('::text').get('').strip()

            json_match = re.findall(r'__PRODUCT_DETAIL_APP_INITIAL_STATE__\s*=\s*(\{.*\});', scr_txt)
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

        option_name = var_item.get('attributeName', '')
        options = [{
            "id": str(var_item['attributeId']) if (var_item.get('attributeId') is not None) else None,
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
                "add_descr": "",
                "weight": None,
                "length": None,
                "width": None,
                "height": None
            }

        specs = []
        add_descr = ""
        weight = None
        length = None
        width = None
        height = None
        for spec in specs_infos:
            k = spec['key']['name']
            if ('Talimatı' in k) or ('Talimatları' in k):
                d = " ".join(spec['description'].strip().split())
                if d:
                    add_descr += f"<tr><th>{k}</th><td>{d}</td></tr>"
            else:
                v = spec['value']['name']
                if k and v:
                    specs.append({
                        "name": k,
                        "value": v
                    })

                    kk = k.lower()
                    vv = v.lower()
                    if ('gramaj' in kk) or ('ağırlık' in kk):
                        weight = self.get_dim(vv, r'(\d+(?:\.\d+)?)\s?(g|kg|gr)\b')
                    elif ('uzunluk' in kk):
                        length = self.get_dim(vv, r'(\d+(?:\.\d+)?)\s?(m|cm)\b')
                    elif ('genişlik' in kk):
                        width = self.get_dim(vv, r'(\d+(?:\.\d+)?)\s?(m|cm)\b')
                    elif ('yükseklik' in kk):
                        height = self.get_dim(vv, r'(\d+(?:\.\d+)?)\s?(m|cm)\b')

        return {
            "specifications": specs if specs else None,
            "add_descr": f'<table class="trendyol-descr">{add_descr}</table>' if add_descr else "",
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
            "sku": str(vi['itemNumber']),
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

            if unit == 'kg':
                return round(val*self.KG_TO_LB, 2)
            if unit in {'g', 'gr'}:
                return round(val*self.G_TO_LB, 2)
            if unit == 'm':
                return round(val*self.M_TO_IN, 2)
            if unit == 'cm':
                return round(val*self.CM_TO_IN, 2)

    def parse(self, response: HtmlResponse):
        # i = response.meta['cookiejar']
        # print(f"{(i+1):_}/{len(self.start_urls):_}".replace("_", "."), response.url)
        
        if response.status == 404:
            print("Product not found", response.url)
            return

        prod_json = self.get_json(response)
        if not prod_json:
            print("No product JSON:", response.url)
            return

        img_list = prod_json.get('images')
        if not img_list:
            print("No images:", response.url)
            return

        price_raw = prod_json.get('price', {}).get('discountedPrice', {}).get('value')
        if price_raw is None:
            print("No price:", response.url)
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
            "url": response.url,
            "source": "Trendyol",
            "product_id": product_id,
            "existence": existence,
            "title": prod_json['name'],
            "title_en": None,
            "description": descr_info+spec_info["add_descr"], # 稍后会变
            "description_en": None,
            "summary": None,
            "sku": product_id,
            "upc": var_parse['upc'],
            "brand": brand,
            "specifications": spec_info['specifications'],
            "categories": categories,
            "images": ";".join(["https://cdn.dsmcdn.com"+img for img in img_list]),
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
            "shipping_fee": 0.00 if prod_json.get('isFreeCargo') else round(39.99/self.exch_rate, 2), # https://www.trendyol.com/yardim/sorular/2002?grup=1
            "shipping_days_min": None,
            "shipping_days_max": None,
            "weight": spec_info['weight'],
            "length": spec_info['length'],
            "width": spec_info['width'],
            "height": spec_info['height']
        }

        yield {
            "item": item,
            # "i": i,
            "video_id": video_id,
            "has_more_descr": has_more_descr
        }

        # if has_more_descr:
        #     descr_api = f'https://apigw.trendyol.com/discovery-web-productgw-service/api/product-detail/{product_id}/html-content?channelId=1'
        #     headers = { **self.headers, 'Referer': response.url }
        #     yield scrapy.Request(descr_api, headers=headers,
        #                          meta={
        #                              "item": item,
        #                              "video_id": video_id
        #                          },
        #                          callback=self.parse_descr_page,
        #                          cb_kwargs={ 'item': item, "video_id": video_id })
        # elif video_id:
        #     item['description'] = descr_info if descr_info else None
        #     video_api = f'https://apigw.trendyol.com/discovery-web-websfxmediacenter-santral/video-content-by-id/{video_id}?channelId=1'
        #     headers = { **self.HEADERS, 'Referer': response.url }
        #     yield scrapy.Request(video_api, headers=headers,
        #                          meta={
        #                              "item": item,
        #                          },
        #                          callback=self.parse_video)
        # else:
        #     item['description'] = descr_info if descr_info else None
        #     yield item

    def clean_descr(self, descr_txt):
        descr = ""
        if isinstance(descr_txt, BeautifulSoup):
            descr_txt = descr_txt.div

        for child in descr_txt.children:
            if isinstance(child, str):
                descr += " ".join(child.strip().split())
            elif isinstance(child, Tag):
                if child.name in {'a', 'script', 'data-src'}:
                    continue
                elif child.name == 'img':
                    src = child.get('data-src', '').replace("{cdn_url}", "https://cdn.dsmcdn.com")
                    if src:
                        descr += f'<img src="{src}">'
                elif child.name == 'br':
                    descr += '<br>'
                else:
                    sub_descr = self.clean_descr(child)
                    if sub_descr:
                        descr += f'<{child.name}>{sub_descr}</{child.name}>'

        return descr

    def parse_descr_page(self, response: HtmlResponse, item, video_id):
        # url = item['url']
        descr_info = item['description']

        descr_page = response.json()['result']
        descr_page = self.clean_descr(BeautifulSoup(descr_page, 'html.parser')) if descr_page else ""
        description = descr_info+descr_page
        item['description'] = description if description else None

        # if video_id:
        #     video_api = f'https://apigw.trendyol.com/discovery-web-websfxmediacenter-santral/video-content-by-id/{video_id}?channelId=1'
        #     headers = { **self.HEADERS, 'Referer': url }
        #     yield scrapy.Request(video_api, headers=headers,
        #                          meta={
        #                              "item": item,
        #                          },
        #                          callback=self.parse_video)
        # else:
        yield item

    def parse_video(self, response: HtmlResponse, item):
        item['videos'] = response.json().get('result', {}).get('url')
        yield item
