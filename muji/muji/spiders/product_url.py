from json import dumps, load
from re import findall

import scrapy
from scrapy.http import HtmlResponse


# scrapy crawl muji_prod_url -O muji_prod_urls.json
class MujiProductUrl(scrapy.Spider):
    name = "muji_prod_url"
    allowed_domains = ["www.muji.com"]
    start_urls = []
    prod_ids = set()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        with open('muji_categories.json', 'r') as f:
            categories = (f)
        self.start_urls = [c['cat_url'] for c in categories]
        print(f'Total {len(self.start_urls):_} categories'.replace("_", "."))

    def get_headers(self, referer: str):
        return {
            "Accept": "*/*",
            # "Accept-Encoding": "gzip, deflate, br, zstd", # 若发现请求回答内容奇怪，试着不用这个请求头
            "Accept-Language": "pt-PT,pt;q=0.8,en-GB;q=0.5,en;q=0.3",
            "Content-Type": "application/json",
            "Referer": referer,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0"
        }
    
    def get_cat_no(self, url: str):
        """
        从URL中提取出分类号
        """
        
        cat_match = findall(r'/cmdty/section/(S[0-9]+)', url)
        if cat_match:
            return cat_match[0]

    def charge_utile(self, cat_no: str, page: int):
        payload = {
            "operationName": "getSectionProducts",
            "variables": {
                "sectionCode": cat_no,
                "sectionItemFilterInput": {
                    "isStockOnly": False,
                    "sizeTexts": [],
                    "colorTexts": [],
                    "minPrice": 0,
                    "maxPrice": None,
                    "priceTypes": [],
                    "isCustomMade": False,
                    "curtainStyles": []
                },
                "sectionItemSort":"new",
                "offset": page
            },
            "query": "query getSectionProducts($sectionCode: String!, $sectionItemFilterInput: SectionItemFilterInput, $sectionItemSort: SectionItemSort, $offset: Int) {\n  sectionItems(\n    input: {sectionCode: $sectionCode, filter: $sectionItemFilterInput, sort: $sectionItemSort, offset: $offset}\n  ) {\n    hasNext\n    products {\n      image {\n        src\n        alt\n        __typename\n      }\n      name\n      description\n      price {\n        max\n        min\n        __typename\n      }\n      colorVariations {\n        colorCode: janCode\n        image {\n          src\n          alt\n          __typename\n        }\n        url\n        colorImage {\n          alt\n          src\n          __typename\n        }\n        colorName\n        janCode\n        hasStock\n        canDirectCartIn\n        price {\n          max\n          min\n          __typename\n        }\n        __typename\n      }\n      labels\n      size\n      isDeliveryFree\n      isBulkItem\n      isLargeAmountItem\n      brand\n      banner\n      link: url\n      janCode\n      webIntensiveCode\n      canDirectCartIn\n      hasStock\n      canAddFavorite\n      __typename\n    }\n    __typename\n  }\n  sectionProductSummary(\n    input: {sectionCode: $sectionCode, filter: $sectionItemFilterInput, sort: $sectionItemSort, offset: $offset}\n  ) {\n    webIntensiveCode\n    janCode\n    name\n    colorVariations {\n      janCode\n      colorCode\n      colorName\n      colorImage {\n        ...ImgFrgs\n        __typename\n      }\n      inventoryStatus\n      inventoryText\n      __typename\n    }\n    colorSizeVariations {\n      colorCode\n      sizeVariations {\n        janCode\n        sizeCode\n        sizeName\n        inventoryStatus\n        __typename\n      }\n      __typename\n    }\n    bulkPurchaseChoices {\n      text\n      bulkCount\n      bulkPrice\n      singlePrice\n      __typename\n    }\n    skuVariations {\n      janCode\n      price\n      image {\n        ...ImgFrgs\n        __typename\n      }\n      colorName\n      colorCode\n      colorImage {\n        ...ImgFrgs\n        __typename\n      }\n      size\n      sizeCode\n      hasStock\n      url\n      directCartInButton {\n        type\n        text\n        __typename\n      }\n      canDirectCartIn\n      __typename\n    }\n    addCartMaxQuantity\n    __typename\n  }\n}\n\nfragment ImgFrgs on Image {\n  alt\n  src\n  __typename\n}"
        }

        return dumps(payload)
    
    def start_requests(self):
        # self.start_urls = ['https://www.muji.com/jp/ja/store/cmdty/section/S1070204?web_store=web_section_lv3_search_by_category'] # test
        for i, cu in enumerate(self.start_urls, start=1):
            print(f"{i:_}".replace('_', '.'), cu)
            cat_no = self.get_cat_no(cu)
            
            yield scrapy.Request('https://www.muji.com/jp/ja/ec-bff/graphql', headers=self.get_headers(cu),
                                 meta={
                                         'cat_url': cu,
                                         'cat_no': cat_no,
                                         'page': 0
                                     },
                                 body=self.charge_utile(cat_no, 0),
                                 method='POST',
                                 callback=self.parse)

    def parse(self, response: HtmlResponse):
        cu = response.meta['cat_url']
        cat_no = response.meta['cat_no']
        page = response.meta['page']

        try:
            contents = response.json()
        except:
            return
        if 'data' not in contents:
            return
        if 'sectionItems' not in contents['data']:
            return

        has_more = contents['data']['sectionItems']['hasNext']
        produits = [item in contents['data']['sectionItems']['products'] if item['__typename'] == 'ProductCard']

        for prod in produits:
            prod_id = prod['janCode']
            if prod_id not in self.prod_ids:
                self.prod_ids.add(prod_id)
                yield {
                    "prod_url": 'https://www.muji.com/jp/ja'+prod['link']
                }

        # 翻页
        if has_more:
            yield scrapy.Request('https://www.muji.com/jp/ja/ec-bff/graphql', headers=self.get_headers(cu),
                                 meta={
                                         'cat_url': cu,
                                         'cat_no': cat_no,
                                         'page': page+1
                                     },
                                 body=self.charge_utile(cat_no, page+1),
                                 method='POST',
                                 callback=self.parse)

    def closed(self, reason):
        # print(self.prod_ids)
        print(f"{len(self.prod_ids):_} unique products".replace('_', '.'))
