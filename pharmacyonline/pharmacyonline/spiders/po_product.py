from html import unescape
from json import load
from re import findall

from datetime import datetime
import scrapy
from scrapy.http import HtmlResponse


# scrapy crawl po_product -O po_products.json
class POProductSpider(scrapy.Spider):
    """
    商品明细页大部分内容为传统HTML，因此可直接用Scrapy抓取
    """

    name = "po_product"
    allowed_domains = ['www.pharmacyonline.com.au']
    start_urls = []

    AUD_RATE = 0.67 # 澳洲元汇率
    CM_TO_IN = 0.393701
    G_TO_LB = 0.002205
    L_TO_LB = 2.204623
    M_TO_IN = 39.37008
    MG_TO_LB = 0.000002

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
            "Accept-Language": "es-ES,es;q=0.8,en-GB;q=0.5,en;q=0.3",
            "Referer": "https://www.google.es",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0"
        }

        with open('po_prod_links.json', 'r') as f:
            produits = load(f)
        self.start_urls = list(set(p['prod_url'] for p in produits))
        print(f'Total {len(self.start_urls):_} unique products'.replace("_", "."))

    def start_requests(self):
        for pu in self.start_urls:
            print(pu)
            yield scrapy.Request(pu, headers=self.headers, meta={ 'url': pu }, callback=self.parse)
    
    def get_weight(self, txt: str):
        weight = None

        # 重量不解析kg（大部分指动物体重）
        match1 = findall(r'\b([\d\.]+)\s*([GgLlMm]+)\s*[Xx]\s*(\d+)\b', txt) # 重量*个数
        match2 = findall(r'\b(\d+)\s*[Xx]\s*([\d\.]+)\s*([GgLlMm]+)\b', txt) # 个数*重量
        match3 = findall(r'\b([\d\.]+)\s*([GgLlMm]+)\b', txt) # 仅重量

        if match1:
            am = float(match1[0][2])
            un = match1[0][1].lower()
            if un == 'l':
                weight = round(float(match1[0][0])*self.L_TO_LB*am, 2)
            elif (un == 'ml') or (un == 'g'):
                weight = round(float(match1[0][0])*self.G_TO_LB*am, 2)
            elif (un == 'mg'):
                weight = round(float(match1[0][0])*self.MG_TO_LB*am, 2)
        elif match2:
            am = float(match2[0][0])
            un = match2[0][2].lower()
            if un == 'l':
                weight = round(float(match2[0][1])*self.L_TO_LB*am, 2)
            elif (un == 'ml') or (un == 'g'):
                weight = round(float(match2[0][1])*self.G_TO_LB*am, 2)
            elif (un == 'mg'):
                weight = round(float(match2[0][1])*self.MG_TO_LB*am, 2)
        elif match3:
            un = match3[0][1].lower()
            if un == 'l':
                weight = round(float(match3[0][0])*self.L_TO_LB, 2)
            elif (un == 'ml') or (un == 'g'):
                weight = round(float(match3[0][0])*self.G_TO_LB, 2)
            elif (un == 'mg'):
                weight = round(float(match3[0][0])*self.MG_TO_LB, 2)
        
        return weight

    def get_dims(self, txt: str) -> list:
        """
        获取商品长宽高
        """

        dims = [None, None, None]
        units = [None, None, None]
        dims_out = [None, None, None]

        match1 = findall(r'\b(\d*\.?\d+)\s*([CcMm]*)\s*[Xx]\s*(\d*\.?\d+)\s*([CcMm]*)\s*[Xx]\s*(\d*\.?\d+)\s*([CcMm]+)\b', txt) # 长*宽*高
        match2 = findall(r'\b(\d*\.?\d+)\s*([CcMm]*)\s*[Xx]\s*([\d*\.?\d+)\s*([CcMm]+)\b', txt) # 长*宽
        match3 = findall(r'\b(\d*\.?\d+)\s*([CcMm]+)\b', txt) # 长

        if match1:
            units[2] = match1[0][5].lower()
            units[1] = match1[0][3].lower() if match1[0][3] else units[2]
            units[0] = match1[0][1].lower() if match1[0][1] else units[1]
            for i in range(3):
                dims[i] = float(match1[0][i*2])
        elif match2:
            units[1] = match2[0][3].lower()
            units[0] = match2[0][1].lower() if match2[0][1] else units[1]
            dims[0] = float(match2[0][0])
            dims[1] = float(match2[0][2])
        elif match3:
            units[0] = match3[0][1].lower()
            dims[0] = float(match3[0][0])

        for i, (d, u) in enumerate(zip(dims, units)):
            if u == 'm':
                dims_out[i] = round(d*self.M_TO_IN, 2)
            elif u == 'cm':
                dims_out[i] = round(d*self.CM_TO_IN, 2)

        return dims_out

    def parse_descr(self, response: HtmlResponse) -> str:
        description = '<div class="po-descr">'

        descr_sel = response.css('div.detailed > div > div.data.item')
        if descr_sel:
            for i, desc_div in enumerate(descr_sel):
                # print(i)
                # print(desc_div.get())
                # print("----------------------------------------------------------------------------------------------------")

                desc_id = desc_div.css('::attr(id)').get()
                if '<script>' in desc_div.get():
                    continue
                if 'reviews' in desc_id:
                    continue
                if 'tab-label' in desc_id:
                    description += f'<h1>{desc_div.css("a::text").get().strip()}</h1>'
                else:
                    description += '<div>'
                    for j, subd in enumerate(desc_div.css('.content > *')):
                        # print(j)
                        # print(subd.get())
                        # print("====================================================================================================")

                        if '<script>' in subd.get():
                            continue
                        if subd.css('::attr(class)') and ('description' in subd.css('::attr(class)').get()):
                            description += '<div class="product attribute description">'
                            for k, ssubd in enumerate(subd.css('.attribute.description > *')):
                                # print(k)
                                # print(ssubd.get())
                                # print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                                
                                if '<script>' in ssubd.get():
                                    continue
                                if 'promotion' in ssubd.css('::attr(class)').get():
                                    continue
                                description += ssubd.get()
                            description += '</div>'
                        else:
                            description += subd.get()
                    description += '</div>'
        
        description += '</div>'
        description = description.replace('\n', ' ').replace('\r', ' ')

        return description

    def parse(self, response: HtmlResponse):
        """
        从下载下来的HTML中解析数据字段\n
        注意事项：
        1. 没有图的商品卖不出去，只能扔掉
        2. 配送资料统一以国内邮寄为准（不考虑国际邮寄）
        """
        
        # print(response.body)
        # print(response.text)

        # 没有图的商品卖不出去，只能扔掉
        images = ""
        # print(response.css('script[type="text/x-magento-init"]::text').getall())
        for scr in response.css('script[type="text/x-magento-init"]::text').getall():
            if 'mage/gallery/gallery' in scr:
                img_match = findall(r'\"full\"\s*:\s*\"([^\"]*)\",', scr)
                if img_match:
                    images = ";".join([img.replace('\\/', '/') for img in img_match if 'thumb_prescription_pharmacy' not in img])
            if images:
                break
        if not images:
            return

        prod_id = response.css('div[itemprop="sku"]::text').get().strip()
        
        existence = True
        exist_resp = response.css('span.status')
        if not (exist_resp and (exist_resp.css('::text').get().strip().lower() == 'in stock')):
            existence = False

        title = unescape(response.css('span.base::text').get().strip())
        description = self.parse_descr(response)
        # print(description+'\n')

        upc = None
        upc_sel = response.css('meta[itemprop="gtin14"]::attr(content)')
        if upc_sel:
            upc = upc_sel.get().strip()
       
        brand = None
        brand_sel = response.css('div.brand::attr(data-brand)')
        if brand_sel:
            brand = brand_sel.get().strip()

        categories = None
        for scr_txt in response.css('script::text').getall():
            if 'ViewContent' in scr_txt:
                cat_match = findall(r'content_category: \"(.*)\"', scr_txt)
                if cat_match:
                    cats_list = cat_match[0].strip().split(',')
                    if 'new' in cats_list[-1].lower():
                        cats_list.pop()
                    categories = " > ".join(cats_list)
            if categories is not None:
                break

        price_aud = float(response.css('meta[property="product:price:amount"]::attr(content)').get().strip())
        price = round(price_aud*self.AUD_RATE, 2)

        reviews = 0
        review_sel = response.css('div#bvseo-aggregateRatingSection > span.bvseo-reviewCount::text')
        if review_sel:
            reviews = int(review_sel.get().strip())
        
        rating = 0.0
        rating_sel = response.css('div#bvseo-aggregateRatingSection > span.bvseo-ratingValue::text')
        if rating_sel:
            rating = round(float(rating_sel.get().strip()), 1)

        weight = self.get_weight(title)
        length, width, height = self.get_dims(title)

        yield {
            "date": datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
            "url": response.meta['url'],
            "source": "Pharmacy Online",
            "product_id": prod_id,
            "existence": existence,
            "title": title,
            "title_en": title,
            "description": description,
            "description_en": None,
            "summary": None,
            "sku": prod_id,
            "upc": upc,
            "brand": brand,
            "specifications": None,
            "categories": categories,
            "images": images,
            "videos": None,
            "price": price,
            "available_qty": 0 if not existence else None,
            "options": None,
            "variants": None,
            "has_only_default_variant": True,
            "returnable": False,
            "reviews": reviews,
            "rating": rating,
            "sold_count": None,
            "shipping_fee": 6.67 if price_aud < 125.00 else 0.00, # https://www.pharmacyonline.com.au/delivery
            "shipping_days_min": None,
            "shipping_days_max": None,
            "weight": weight,
            "length": length,
            "width": width,
            "height": height
        }
