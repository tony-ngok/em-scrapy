# 使用上级目录中的utils
import sys
sys.path.append('..')

from datetime import datetime
from json import loads
from re import findall

# import requests
from bs4 import BeautifulSoup, Tag
import scrapy
from scrapy.http import HtmlResponse


# scrapy crawl monotaro_product
class MonotaroProduct(scrapy.Spider):
    name = "monotaro_product"
    allowed_domains = ["www.monotaro.com"]
    start_urls = []

    HEADERS = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
        "Accept-Language": "pt-PT,pt;q=0.8,en-GB;q=0.5,en;q=0.3",
        "Referer": "https://www.google.pt",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0"
    }

    custom_settings = {
        "ITEM_PIPELINES": {
            "utils.mongodb.pipelines.pipeline1.MongoPipeLine1": 400,
        }
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # with open('monotaro_prod_urls.txt', 'r') as f:
        #     for line in f:
        #         if line.strip():
        #             self.start_urls.append(line.strip())
        # print(f'Total {len(self.start_urls):_} products'.replace("_", "."))

        self.jpy_rate = 153.237093
        # try:
        #     resp = requests.get('https://open.er-api.com/v6/latest/USD')
        #     if resp.ok:
        #         self.jpy_rate = resp.json()['rates']['JPY']
        #     else:
        #         raise Exception(f'Status {resp.status_code}')
        # except Exception as e:
        #     print("Fail to get latest USD/JPY rate", str(e))
        # finally:
        #     print(f"USD/JPY rate: {self.jpy_rate:_}".replace(".", ",").replace("_", "."))

    def get_prod_url(self, prod_id: str, p: int = 1):
        if p > 1:
            return f'https://www.monotaro.com/g/{prod_id}/page-{p}/'
        return f'https://www.monotaro.com/g/{prod_id}/'

    def get_basic_descr(self, response):
        basic_descr = ""

        if isinstance(response, HtmlResponse):
            response = BeautifulSoup(response.css('p.DescriptionText').get(''), "html.parser")
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
        weight = None
        length = None
        width = None
        height = None

        spans = response.css('span.AttributeLabel__Wrap').getall()
        for span in spans:
            if span:
                span = BeautifulSoup(span, 'html.parser')
                span = span.span

                spec_name = ''
                spec_val = ''
                is_add_descr = False

                for child in span.children:
                    if isinstance(child, Tag) and (child.name == 'span'):
                        spec_name = child.text.strip()
                        if (spec_name in {'用途', '使用方法', '機能', '内容'}) or ('成分' in spec_name) or ('材質' in spec_name):
                            is_add_descr = True
                    elif isinstance(child, Tag) and (child.name == 'div'): # 较长的参数值放入描述中
                        is_add_descr = True
                        spec_val = " ".join(child.text.strip().replace("\n", '<br>').split())
                    elif isinstance(child, str) and child.strip():
                        if "。" in spec_val:
                            is_add_descr = True
                        spec_val = child.strip()

                if spec_name and spec_val:
                    if is_add_descr:
                        add_descr += f'<tr><th>{spec_name}</th><td>{spec_val}</td></tr>'
                    else:
                        specs.append({
                            "name": spec_name,
                            "value": spec_val
                        })

                        if spec_name in {'質量(g)', '重量(g)'}:
                            weight = self.parse_weight(spec_val, 'g')
                        elif spec_name in {'質量(kg)', '重量(kg)'}:
                            weight = self.parse_weight(spec_val, 'kg')
                        else:
                            if spec_name == '寸法(Φ×mm)':
                                length, width, height = self.parse_dims(spec_val, 'mm', True)
                            elif spec_name == '寸法(mm)':
                                length, width, height = self.parse_dims(spec_val, 'mm', spec_val.startswith('Φ'))
                            elif spec_name == '寸法(Φ×cm)':
                                length, width, height = self.parse_dims(spec_val, 'cm', True)
                            elif spec_name == '寸法(cm)':
                                length, width, height = self.parse_dims(spec_val, 'cm', spec_val.startswith('Φ'))
                            elif spec_name == '寸法(Φ×m)':
                                length, width, height = self.parse_dims(spec_val, 'm', True)
                            elif spec_name == '寸法(m)':
                                length, width, height = self.parse_dims(spec_val, 'm', spec_val.startswith('Φ'))
                            else:
                                if length is None:
                                    if spec_name == '長さ(m)':
                                        length = self.parse_weight(spec_val, 'm')
                                    elif spec_name == '長さ(cm)':
                                        length = self.parse_weight(spec_val, 'cm')
                                    elif spec_name == '長さ(mm)':
                                        length = self.parse_weight(spec_val, 'mm')
                                if width is None:
                                    if spec_name == '幅(m)':
                                        width = self.parse_weight(spec_val, 'm')
                                    elif spec_name == '幅(cm)':
                                        width = self.parse_weight(spec_val, 'cm')
                                    elif spec_name == '幅(mm)':
                                        width = self.parse_weight(spec_val, 'mm')
                                if height is None:
                                    if spec_name == '高さ(m)':
                                        height = self.parse_weight(spec_val, 'm')
                                    elif spec_name == '高さ(cm)':
                                        height = self.parse_weight(spec_val, 'cm')
                                    elif spec_name == '高さ(mm)':
                                        height = self.parse_weight(spec_val, 'mm')

        return (specs if specs else None), add_descr, weight, length, width, height

    def parse_weight(self, w_text: str, unit: str):
        w_match = findall(r'(\d+(?:\.\d+)?)', w_text)
        if w_match and (len(w_match) == 1):
            if unit == 'g':
                return round(float(w_match[0])*0.002205, 2)
            elif unit == 'kg':
                return round(float(w_match[0])*2.20462, 2)
            elif unit == 'm':
                return round(float(w_match[0])*39.37008, 2)
            elif unit == 'cm':
                return round(float(w_match[0])*0.393701, 2)
            elif unit == 'mm':
                return round(float(w_match[0])*0.0393701, 2)
        return None

    def parse_dims(self, dims_text: str, unit: str, is_diam: bool = False):
        """
        提取商品长、宽、高（寸法）\n
        支援以下格式：
        * 长×宽×高
        * 长×宽
        * 直径×高\n
        不支援参数不明的单个数值
        """

        match1 = findall(r'(\d+(?:\.\d+)?)\s*×\s*(\d+(?:\.\d+)?)\s*×\s*(\d+(?:\.\d+)?)', dims_text)
        if match1 and (len(match1) == 1):
            l, w, h = match1[0]
            if unit == 'm':
                return round(float(l)*39.37008, 2), round(float(w)*39.37008, 2), round(float(h)*39.37008, 2)
            elif unit == 'cm':
                return round(float(l)*0.393701, 2), round(float(w)*0.393701, 2), round(float(h)*0.393701, 2)
            elif unit == 'mm':
                return round(float(l)*0.0393701, 2), round(float(w)*0.0393701, 2), round(float(h)*0.0393701, 2)

        match2 = findall(r'(\d+(?:\.\d+)?)\s*×\s*(\d+(?:\.\d+)?)', dims_text)
        if match2 and (len(match2) == 1):
            d1, d2 = match2[0]
            if is_diam:
                if unit == 'm':
                    return round(float(d1)*39.37008, 2), round(float(d1)*39.37008, 2), round(float(d2)*39.37008, 2)
                elif unit == 'cm':
                    return round(float(d1)*0.393701, 2), round(float(d1)*0.393701, 2), round(float(d2)*0.393701, 2)
                elif unit == 'mm':
                    return round(float(d1)*0.0393701, 2), round(float(d1)*0.0393701, 2), round(float(d2)*0.0393701, 2)
            else:
                if unit == 'm':
                    return round(float(d1)*39.37008, 2), round(float(d2)*39.37008, 2), None
                elif unit == 'cm':
                    return round(float(d1)*0.393701, 2), round(float(d2)*0.393701, 2), None
                elif unit == 'mm':
                    return round(float(d1)*0.0393701, 2), round(float(d2)*0.0393701, 2), None

        return None, None, None

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
        imgx = response.css('div.ImgFixedSizeModalMain__Item > img::attr(src)').getall()
        img_list = ['https:'+img for img in imgx if img and 'mono_image_na' not in img]
        return ";".join(img_list) if img_list else None

    def get_videos(self, response: HtmlResponse):
        vidx = response.css('div.MovieContents__Iframe > iframe::attr(src)').getall()
        vid_list = [vid.split('?')[0] for vid in vidx if vid]
        return ";".join(vid_list) if vid_list else None

    def get_raw_vars(self, response: HtmlResponse):
        """
        从表格（至少一行）中获得所有变种资料
        """

        raw_vars_info = {} # 键代表属性名，值列表代表属性值

        col_names = response.css('div.ProductsDetails thead th')

        # 获得有效列（商品画像、SKU码、变种选项名、价格、库存状况）
        valid_cols = {}
        for i, th in enumerate(col_names):
            if th.css(':scope div.SortCell__Title'): # 变种选项
                th_raw = th.css(':scope div.SortCell__Title').get('')
                th_soup = BeautifulSoup(th_raw, 'html.parser')
                th_txt = th_soup.text.strip()

                valid_cols[th_txt] = i
                raw_vars_info[th_txt] = []
            else: # 变种基本资料
                th_txt = th.css('::text').get('').strip()
                if th_txt:
                    if th_txt == '商品画像':
                        valid_cols['image'] = i
                        raw_vars_info['image'] = []
                    elif th_txt == '注文コード':
                        valid_cols['variant_id'] = i
                        raw_vars_info['variant_id'] = []
                    elif (th_txt == '販売価格') and ('Table__HeadCell--GpagePrice' in th.css('::attr(class)').get('').split()):
                        valid_cols['price'] = i
                        raw_vars_info['price'] = []
                    elif th_txt == '出荷目安':
                        valid_cols['available_qty'] = i
                        raw_vars_info['available_qty'] = []

        # 积累有效列资料
        rows = response.css('div.ProductsDetails tbody > tr')
        for row in rows:
            rcols = row.css('td')

            for k, v in valid_cols.items():
                var_spec = None

                if k == 'image':
                    var_spec = rcols[v].css('div.SKUProductImage img::attr(src)').get()
                    if var_spec:
                        var_spec = 'https:'+var_spec
                elif k == 'variant_id':
                    var_spec = rcols[v].css('a::text').get('-')
                elif k == 'price':
                    var_spec = rcols[v].css(':scope span.Price--Md::text').get()
                    if not var_spec:
                        var_spec = 'SKIP_VAR'
                    else:
                        var_spec = int(var_spec.replace(',', ''))
                elif k == 'available_qty':
                    if rcols[v].css(':scope span[title="取扱い終了"]'):
                        var_spec = 'SKIP_VAR'
                    elif rcols[v].css(':scope span[title="欠品中"]'):
                        var_spec = 0
                else:
                    var_spec = rcols[v].css('::text').get('').strip()

                raw_vars_info[k].append(var_spec)

        return raw_vars_info

    def get_opts_vars(self, raw_vars_info: dict):
        """
        整理获得的变种资料为标准格式
        """

        options = []
        for k in raw_vars_info:
            if (k == '品番') and (raw_vars_info['品番'][0] == '-'): # 实际上无“品番”选项之情况
                continue
            elif k not in {'image', 'variant_id', 'price', 'available_qty'}:
                options.append(k)

        variants = []
        total_vars = len(raw_vars_info['variant_id'])
        for i in range(total_vars):
            if (raw_vars_info['price'][i] != 'SKIP_VAR') and (raw_vars_info['available_qty'][i] != 'SKIP_VAR'):
                variant = {
                    "variant_id": raw_vars_info['variant_id'][i],
                    "barcode": None,
                    "sku": raw_vars_info['variant_id'][i],
                    "option_values": [{
                        "option_id": None,
                        "option_value_id": None,
                        "option_name": opt,
                        "option_value": raw_vars_info[opt][i]
                    } for opt in options],
                    "images": raw_vars_info['image'][i] if raw_vars_info.get('image') else None,
                    "price": raw_vars_info['price'][i], # 稍后再汇率换算
                    "available_qty": raw_vars_info['available_qty'][i]
                }
                variants.append(variant)

        options = [{
            "id": None,
            "name": opt
        } for opt in options] if options else None
        return options, variants

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
        print(f"{i:_}/{len(self.start_urls):_}".replace(".", ","), response.url)

        if p == 1: # 提取基本商品资料（包含最初50个变种）
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

            raw_vars = self.get_raw_vars(response)
            item['options'], variants = self.get_opts_vars(raw_vars)
            if not variants:
                print("Product end", response.url)
                return

            item['url'] = response.url
            item['source'] = 'MonotaRO'
            item['product_id'] = pid

            item['specifications'], add_descr, item['weight'], item['length'], item['width'], item['height'] = self.get_specs_etc(response)
            basic_descr = self.get_basic_descr(response)
            alert_descr = self.get_alert_descr(response)
            item['description'] = self.combine_descr(basic_descr, add_descr, alert_descr)

            item['title_en'] = None
            item['description_en'] = None
            item['summary'] = None
            item['upc'] = None
            item['brand'] = self.get_brand(prod_json)
            item['categories'] = self.get_cats(bc_json)
            item['videos'] = self.get_videos(response)

            item['existence'] = (variants[0]['available_qty'] is None)
            item['available_qty'] = variants[0]['available_qty']
            item['sku'] = variants[0]['variant_id']

            price_jpy = variants[0]['price']
            item['shipping_fee'] = round(500/self.jpy_rate, 2) if price_jpy < 3500 else 0.00
            item['price'] = round(price_jpy/self.jpy_rate, 2)

            for j, v in enumerate(variants):
                variants[j]['price'] = round(v['price']/self.jpy_rate, 2)
            item['variants'] = variants

            item['returnable'] = False
            item['reviews'], item['rating'] = self.get_recensions(prod_json)
            item['sold_count'] = None

            # https://help.monotaro.com/app/answers/detail/a_id/13
            item['shipping_days_min'] = 1
            item['shipping_days_max'] = 10
        else: # 变种超过50个：继续提取变种
            raw_vars = self.get_raw_vars(response)
            _, variants = self.get_opts_vars(raw_vars)
            for j, v in enumerate(variants):
                variants[j]['price'] = round(v['price']/self.jpy_rate, 2)
            item['variants'].extend(variants)

        more_vars = response.css('a.Button--PaginationNext')
        if more_vars:
            # next_purl = self.get_prod_url(pid, p+1)
            # headers = { **self.HEADERS, 'Referer': response.url }
            # yield scrapy.Request(next_purl, headers=headers,
            #                      meta={ 'cookiejar': response.meta['cookiejar'] },
            #                      callback=self.parse,
            #                      cb_kwargs={ 'i': i+1, "pid": pid, "p": p+1, "item": item })
            yield item
        else:
            item['variants'] = item['variants'] if item['options'] and item['variants'] else None # 变种提取结束
            item['has_only_default_variant'] = not (item['variants'] and (len(item['variants']) > 1))
            item['date'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
            yield item
