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
            # "Accept-Encoding": "gzip, deflate, br, zstd", # 请求返回无法阅读的压缩内容：不要这个请求头了
            "Accept-Language": "es-ES,es;q=0.8,en-GB;q=0.5,en;q=0.3",
            "Referer": "https://www.google.es",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0"
        }

        # with open('po_prod_links.json', 'r') as f:
        #     produits = load(f)
        # self.start_urls = list(set(p['prod_url'] for p in produits))
        
        self.start_urls = [
            "https://www.pharmacyonline.com.au/go-healthy-go-beautiful-skin-collagen-support-cap-x-60",
            "https://www.pharmacyonline.com.au/novasone-ointment-0-1-15g",
            "https://www.pharmacyonline.com.au/hongyu-disposable-face-masks-black-x-50",
            "https://www.pharmacyonline.com.au/weleda-mother-nursing-tea-bags-x-20",
            "https://www.pharmacyonline.com.au/hot-hands-cura-heat-neck-shoulder-tension-therapeutic-heat-patch-1-pack",
            "https://www.pharmacyonline.com.au/restavit-25mg-tab-x-20",
            "https://www.pharmacyonline.com.au/dr-wolff-s-v-san-lactic-acid-pessaries-x-7",
            "https://www.pharmacyonline.com.au/gevity-bone-broth-body-glue-a-m-cleanse-390g",
            "https://www.pharmacyonline.com.au/osteomol-tablet-665mg-x-96-paracetamol",
            "https://www.pharmacyonline.com.au/phenergan-10mg-tab-x-50",
            "https://www.pharmacyonline.com.au/classic-floral-talcum-powder-250g",
            "https://www.pharmacyonline.com.au/asmol-cfc-free-inhaler-100mcg-x-200-dose-generic-for-ventolin",
            "https://www.pharmacyonline.com.au/hydroxocobalamin-injection-x-3-ampoules",
            "https://www.pharmacyonline.com.au/polaramine-6-hour-2mg-tab-x-25-1",
            "https://www.pharmacyonline.com.au/eurax-cream-for-itches-20g",
            "https://www.pharmacyonline.com.au/allertine-bilastine-20mg-tab-x-10",
            "https://www.pharmacyonline.com.au/spring-rose-talcum-powder-250g",
            "https://www.pharmacyonline.com.au/picoprep-sachets-x-3",
            "https://www.pharmacyonline.com.au/cause-im-happy-face-mask-hearts-x-10",
            "https://www.pharmacyonline.com.au/epipen-trainer",
            "https://www.pharmacyonline.com.au/phenergan-25mg-tab-x-50",
            "https://www.pharmacyonline.com.au/vitapointe-between-wash-conditioner-30g",
            "https://www.pharmacyonline.com.au/hot-hands-toe-warmers-5-pairs",
            "https://www.pharmacyonline.com.au/nuromol-tab-x-24-paracetamol-and-ibuprofen",
            "https://www.pharmacyonline.com.au/bellamy-s-organic-step-1-infant-formula-900g",
            "https://www.pharmacyonline.com.au/maxalt-migraine-relief-rizatriptan-5mg-tab-x-2",
            "https://www.pharmacyonline.com.au/bellamy-s-organic-step-2-follow-on-formula-900g",
            "https://www.pharmacyonline.com.au/bisacodyl-suppositories-x-10-generic-for-dulcolax",
            "https://www.pharmacyonline.com.au/ferrous-c-iron-supplement-cap-x-30",
            "https://www.pharmacyonline.com.au/softmed-fog-free-fluid-resistant-level-3-earloop-surgical-face-mask-x-50",
            "https://www.pharmacyonline.com.au/hot-hands-body-hand-super-warmer-5-pack",
            "https://www.pharmacyonline.com.au/prolistat-120mg-cap-x-84",
            "https://www.pharmacyonline.com.au/differin-acne-treatment-cream-30g",
            "https://www.pharmacyonline.com.au/hot-hands-hand-warmers-1-pair",
            "https://www.pharmacyonline.com.au/xylocaine-5-ointment-15g",
            "https://www.pharmacyonline.com.au/xenical-cap-120mg-x-42-2-week-supply",
            "https://www.pharmacyonline.com.au/dr-wolff-s-v-san-intimate-wash-lotion-200ml",
            "https://www.pharmacyonline.com.au/hot-hands-adhesive-body-warmer-1-pack",
            "https://www.pharmacyonline.com.au/melotin-mr-melatonin-2mg-tab-x-15-non-prescription-for-age-55-only",
            "https://www.pharmacyonline.com.au/moviprep-powder-sachet-orange-100g",
            "https://www.pharmacyonline.com.au/vacuum-erection-device",
            "https://www.pharmacyonline.com.au/hydrozole-cream-1-30g",
            "https://www.pharmacyonline.com.au/fluconazole-one-cap-150mg-x-1-generic-for-diflucan-canesoral",
            "https://www.pharmacyonline.com.au/h2o-trojan-vibrator-lavender",
            "https://www.pharmacyonline.com.au/dr-wolff-s-v-san-moisturising-cremolum-pessaries-x-16",
            "https://www.pharmacyonline.com.au/invite-e-vitamin-e-cream-50g",
            "https://www.pharmacyonline.com.au/periactin-4mg-tab-x-100",
            "https://www.pharmacyonline.com.au/picoprep-sachets-x-2",
            "https://www.pharmacyonline.com.au/hot-hands-body-hand-super-warmer-1-pack",
            "https://www.pharmacyonline.com.au/famciclovir-tab-500mg-x-3",
            "https://www.pharmacyonline.com.au/allersoothe-10mg-tab-x-50",
            "https://www.pharmacyonline.com.au/polaramine-6-hour-2mg-tab-x-25",
            "https://www.pharmacyonline.com.au/allertine-bilastine-20mg-tab-x-30",
            "https://www.pharmacyonline.com.au/moviprep-powder-sachet-100g",
            "https://www.pharmacyonline.com.au/feichan-disposable-protective-disposable-face-mask-black-x-50",
            "https://www.pharmacyonline.com.au/saltabs-600mg-salt-tab-x-100",
            "https://www.pharmacyonline.com.au/face-shield-blue",
            "https://www.pharmacyonline.com.au/baremedical-n-95-vertical-flat-fold-earloop-face-mask-x-10",
            "https://www.pharmacyonline.com.au/creon-micro-granules-20g",
            "https://www.pharmacyonline.com.au/bricanyl-turbuhaler-500mcg-x-120-doses",
            "https://www.pharmacyonline.com.au/hot-hands-cura-heat-menstrual-cramp-therapeutic-heat-patch-1-pack",
            "https://www.pharmacyonline.com.au/lax-suppositories-bisacodyl-10mg-x-10",
            "https://www.pharmacyonline.com.au/xylocaine-viscous-solution-200ml",
            "https://www.pharmacyonline.com.au/baremedical-level-3-earloop-surgical-face-mask-x-50",
            "https://www.pharmacyonline.com.au/hiprex-urinary-tract-antibacterial-tab-x-100-1",
            "https://www.pharmacyonline.com.au/pantoprazole-tab-20mg-x-7-generic-for-somac",
            "https://www.pharmacyonline.com.au/cortic-ds-1-ointment-30g-generic-for-sigmacort",
            "https://www.pharmacyonline.com.au/somac-heartburn-relief-tab-x-14",
            "https://www.pharmacyonline.com.au/dr-wolff-s-v-san-moisturising-cream-50g",
            "https://www.pharmacyonline.com.au/hot-hands-toasti-toes-toe-warmers-1-pair",
            "https://www.pharmacyonline.com.au/chlorsig-eye-ointment-4g",
            "https://www.pharmacyonline.com.au/dozile-tab-x-20",
            "https://www.pharmacyonline.com.au/phenergan-elixir-5mg-5ml-100ml",
            "https://www.pharmacyonline.com.au/q-a-vitamin-a-c-e-cleansing-shower-oil-250ml",
            "https://www.pharmacyonline.com.au/nilstat-oral-drops-24ml-nystatin",
            "https://www.pharmacyonline.com.au/circadin-tab-2mg-x-30-melatonin-age-55-only",
            "https://www.pharmacyonline.com.au/differin-acne-treatment-gel-30g",
            "https://www.pharmacyonline.com.au/ventolin-cfc-free-inhaler-100mcg-x-200-dose",
            "https://www.pharmacyonline.com.au/allersoothe-tab-25mg-x-50-promethazine",
            "https://www.pharmacyonline.com.au/kenalog-in-orabase-for-mouth-ulcers-5g",
            "https://www.pharmacyonline.com.au/zaditen-eye-drops-0-4ml-x-20",
            "https://www.pharmacyonline.com.au/infrared-forehead-thermometer",
            "https://www.pharmacyonline.com.au/2san-lyher-covid-19-sars-cov-2-rapid-antigen-test-rats-nasal-x-1",
            "https://www.pharmacyonline.com.au/creon-10000-cap-x-100",
            "https://www.pharmacyonline.com.au/go-healthy-go-hemp-seed-oil-1100mg-cap-x-100",
            "https://www.pharmacyonline.com.au/medomics-covid-19-sars-cov-2-rapid-antigen-test-rats-nasal-x-5",
            "https://www.pharmacyonline.com.au/abbott-freestyle-freedom-glucose-monitoring-kit",
            "https://www.pharmacyonline.com.au/melatonin-2mg-tab-x-30-age-55-only",
            "https://www.pharmacyonline.com.au/xenical-cap-120mg-x-84-1-month-supply",
            "https://www.pharmacyonline.com.au/nitrolingual-pumpspray-400mcg-x-200-doses",
            "https://www.pharmacyonline.com.au/luvloob-are-you-keen-natural-oil-based-lubricant-chocolate-flavour-75ml",
            "https://www.pharmacyonline.com.au/pantoprazole-tab-20mg-x-14",
            "https://www.pharmacyonline.com.au/hydrogen-peroxide-200ml",
            "https://www.pharmacyonline.com.au/hot-hands-hand-warmers-5-pairs",
            "https://www.pharmacyonline.com.au/lomide-eye-drops-10ml",
            "https://www.pharmacyonline.com.au/prepkit-orange",
            "https://www.pharmacyonline.com.au/imigran-migraine-50mg-tab-x-2",
            "https://www.pharmacyonline.com.au/lavender-talcum-powder-250g",
            "https://www.pharmacyonline.com.au/weleda-calendula-soap-bar-100g",
            "https://www.pharmacyonline.com.au/fleurstat-bv-gel-45g",
            "https://www.pharmacyonline.com.au/cellife-covid-19-antigen-test-cassette-5-tests",
            "https://www.pharmacyonline.com.au/paracetamol-osteo-tab-tab-x-96-generic-for-panadol-osteo",
            "https://www.pharmacyonline.com.au/h2o-patriot-vibrator-lavender",
            "https://www.pharmacyonline.com.au/zaditen-eye-drops-5ml",
            "https://www.pharmacyonline.com.au/hiprex-urinary-tract-antibacterial-tab-x-20",
            "https://www.pharmacyonline.com.au/cortic-ds-1-cream-30g-generic-for-sigmacort",
            "https://www.pharmacyonline.com.au/h2o-g-spot-probe-vibrator-pink",
            "https://www.pharmacyonline.com.au/novasone-cream-0-1-15g",
        ]
        
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

        descr_sel = response.css('div.detailed > div > div')
        if descr_sel:
            for i, desc_div in enumerate(descr_sel):
                # print(i)
                # print(desc_div.get())
                # print("----------------------------------------------------------------------------------------------------")
                desc_id = desc_div.css('::attr(id)').get()
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
                            for k, ssubd in enumerate(subd.css('.description > *')):
                                # print(k)
                                # print(ssubd.get())
                                # print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
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
