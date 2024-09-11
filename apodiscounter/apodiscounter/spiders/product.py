import json
import re
from datetime import datetime
from urllib.parse import urlparse

from bs4 import BeautifulSoup
# from em_product.product import StandardProduct
# from fp.fp import FreeProxy
import scrapy
from scrapy.http import HtmlResponse
import scrapy.selector


# scrapy crawl product -O apodiscounter_produkte.json
class ProductSpider(scrapy.Spider):
    name = "product"
    allowed_domains = ["apodiscounter.de"]
    start_urls = []

    EXCHANGE_RATE_EUR_TO_US = 1.1024

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # self.cookies = {
        #     "_ALGOLIA": "anonymous-2d511032-566d-4c70-9e39-0da8a959883f",
        #     "baqend-speedkit-config": '{"group":"A","testId":"50vs50_2024_09_02"}',
        #     "baqend-speedkit-user-id": "OErThTWKUGmjDsqUvOqI4PEvj",
        #     "cf_clearance": "X1c_z7qlslGSAJzF29rvUu04DOhutxgjZ5yLoeI6icw-1726078626-1.2.1.1-14QNfH7EQtfY4CJKtwPjGCJf8AW6LSywnwj0bLFRJHnSdbbDNAopPhoWef4GtiwkTEc8jLeJkfL_M.pAxzx5dVCGwIrHRIkhUcH2J63FU05D35G7jbVAscGBrzuANr7xIOB5e1pzA82syB1QA0HF0PjWHgOSWiY9Iq0E0Cv3F4fEM.gwx_3X0Cu968GMUfoWd0PKPgs2N3ts4cKZGlvZet1acXvEvl9Bpe6p6rkaFvEQ7OHYYil_m91VK3ixMIwJdzb13uIE0hBsVD1ZD0BxLGe3yX6YyzhEHqdSZ8OEpECUd2JMvNca1dY2avmq2e_.LMvHzWQh4IFHtITpR9txWvgJj0UHszpSSKA_ciUWrOE",
        #     "CSS_STATUS": "is_loaded",
        #     "desiredTemplate": "desktop",
        #     "XTCsid": "2888878f6924e1b229d7927f90ba5ef1"
        # }

        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
            # "Accept-Encoding": "gzip, deflate, br, zstd", # 若发现请求回答内容奇怪，试着不用这个请求头
            "Accept-Language": "de-DE,de;q=0.8,en-GB;q=0.5,en;q=0.3",
            "Referer": "https://www.google.de",
            "Sec-Ch-Ua-Platform": "\"Windows\"",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0"
        }

        with open('apodiscounter_produkturls.json', 'r') as f:
            produits = json.load(f)
        self.start_urls = [p['prod_url'] for p in produits]
        print(f'Insgesamt {len(self.start_urls):_} Produkt(e)'.replace("_", "."))

    def start_requests(self):
        self.start_urls = ['https://www.apodiscounter.de/voltactive-kniebandage-s-1stk-pzn-16506658']
        for i, url in enumerate(self.start_urls, start=1):
            print(i, url)
            # proxy = FreeProxy(https=True, rand=True).get()
            # print(proxy)
            # meta = { 'proxy': proxy } if proxy else None

            yield scrapy.Request(url,
                # meta=meta,
                headers=self.headers,
                # cookies=self.cookies,
                callback=self.parse,
                errback=self.errback,
            )

    def get_product_data(self, response: HtmlResponse):
        product_data = None
        script_list = response.xpath("//script[@type='application/ld+json']/text()").getall()

        for script in script_list:
            # print(script)
            try:
                data = json.loads(script)
            except Exception:
                pass
            finally:
                if "@type" in data:
                    if data["@type"] == "Product":
                        product_data = data
                        break

        return product_data

    def get_global_product_data(self, response: HtmlResponse):
        data = response.xpath("//script[contains(text(), 'global_product_datasets')]/text()").get()
        if not data:
            return None

        st_off = data.find("{")
        ed_off = data.rfind("}")

        if st_off != ed_off:
            dict_data = json.loads(data[st_off : ed_off + 1])
            return dict_data

        return None

    def get_sku(self, url):
        sku = None
        parse_usl = urlparse(url)
        split_path = parse_usl.path.split("/")
        if split_path is not None:
            split_dash = split_path.pop().split("-")
            if split_dash is not None:
                sku = split_dash.pop()
        return sku

    def get_source(self, url):
        return "Apodiscounter"

    def get_brand(self, response, product_id):
        brand = None

        global_data = self.get_global_product_data(response)
        if not global_data:
            return None
        brand = global_data[product_id]["brand"]

        if brand is not None:
            if len(brand) < 1:  # in case brand == ""
                brand = None

        return brand

    """
    def get_product_id(self, url):
        pro_id = None
        parse_usl = urlparse(url)
        split_path = parse_usl.path.split("/")
        if(split_path is not None):
            split_dash = split_path.pop().split("-")
            if(split_dash is not None):
                pro_id = split_dash.pop()
        return pro_id
    """

    def get_product_id(self, response: HtmlResponse):
        product_id = None

        global_data = self.get_global_product_data(response)

        if len(global_data.keys()) > 1:
            print(
                "not expected number of product id, num product id :{}".format(
                    len(global_data.keys())
                )
            )

        for product_id_in_data in global_data.keys():
            product_id = product_id_in_data
            break

        return product_id

    def get_title(self, product_data: str):
        # product_data = self.get_product_data(response)
        if not product_data:
            return None
        return product_data["name"]

    def get_price(self, product_data: dict):
        f_price_us = None
        # product_data = self.get_product_data(response)
        f_value = float(product_data["offers"]["price"])

        f_price_us = round(f_value * self.EXCHANGE_RATE_EUR_TO_US, 2)
        return f_price_us

    def get_shipping_fee(self, response: HtmlResponse):
        shipping_fee = None

        shipping_cost_text = response.xpath(
            "//div[@class='product_info_shipping_costs_information']/text()"
        ).get()

        if "Gratis" in shipping_cost_text and "Versand" in shipping_cost_text:
            shipping_fee = 0

        return shipping_fee

    def get_description(self, response: HtmlResponse):
        description = '<div class="apodiscounter-descr">'

        tags = response.css('section.product_description > div').getall()
        # print(tags)

        for tag in tags:
            if 'products_description_manufacturer' not in tag:
                description += tag.replace('\n', '').replace('\r', '').replace('\xa0', '&nbsp;')

        description += '</div>'
        # print(description)
        return description

    def get_videos(self, response: HtmlResponse):
        """
        获得商品影片（从选择器"div#gallery_products_video"判断最多只有一个）
        """

        # videos = None
        # script_list = response.xpath("//script[@type='application/ld+json']/text()").getall()

        # for script in script_list:
        #     try:
        #         data = json.loads(script)
        #     except Exception:
        #         pass
        #     finally:
        #         if isinstance(data, dict) and ("@type" in data):
        #             if data["@type"] == "VideoObject":
        #                 videos = data["@id"]
        #                 break
        #         elif isinstance(data, list):
        #             print("THERE ARE MULTIPLE VIDEOS, NEED PARSE THEM")
        #             breakpoint()

        videos = response.css('div#gallery_products_video > video > source[type="video/webm"]::attr(src)').get()
        return videos

    def get_options(self, product_data: dict):
        options = None # 该站的所谓变种其实有不同商品URL及商品号
        if product_data is None:
            return None

        # product_data = self.get_product_data(response)

        if type(product_data["offers"]) is type(list()):
            print("THERE ARE MULTIPLE OFFERS, NEED PARSE CODE FOR OPTIONS")
            breakpoint()
        elif type(product_data["offers"]) is type(dict()):
            options = None

        return options

    def get_rating(self, response: HtmlResponse):
        f_rating = None

        try:
            value = response.xpath(
                "//div[@class='product_review_rating_all_box_count']/text()"
            ).get()
        except Exception:
            pass
        finally:
            if value is not None:
                f_rating = float(value)

        return f_rating

    def get_reviews(self, response: HtmlResponse):
        reviews = None

        tag = response.css('div.product_review_feedback_rating_count_all::text').get()
        if tag:
            reviews = int(tag.strip()[1:-1])

        return reviews

    def get_preparation_days(self, response: HtmlResponse):
        days = []
        tag = response.xpath(
            "//div[@class='product_info_shipping_information']//div[@class='product_status_box']/span[@class='product_status_link']"
        ).get()
        soup = BeautifulSoup(tag, "html.parser")
        spans = soup.find_all("span")

        for span in spans:
            text_all = span.text.strip()

            if "sofort" in text_all and "lieferbar" in text_all:
                days = [1, 2]
            else:
                values = re.findall(r"(?:\d*)", text_all)
                rets = []
                for x in values:
                    if x.isdigit():
                        rets.append(int(x))
                if len(rets) == 2:
                    if rets[0] < rets[1]:
                        days = [rets[0], rets[1]]
                    else:
                        days = [rets[1], rets[0]]
            if days:
                break

        return days

    def errback(self, failure):
        self.logger.error(failure.value.response.headers)
        self.logger.error(f"{failure.request.url}: {repr(failure)}")

    def parse(self, response: HtmlResponse):
        # print(response.headers)
        # print(response.url)
        # print("==================================================================================================================================")

        self.logger.info(f"{response.url}: {response.status}")
        if response.status > 300:
            return None
        images = response.css('div.product_image_50_50 > img::attr(src)').getall()
        if not images:
            print("Produkt ohne Bilder ignoriert")
            return None

        product_data = self.get_product_data(response) # 这个JSON有时会读不到？
        # print(product_data)

        item = {}

        item["url"] = response.url
        item["date"] = datetime.now().replace(microsecond=0).isoformat()
        item["existence"] = True if response.status == 200 else False

        func_postfix_list_1 = ["sku", "source"]
        for postfix in func_postfix_list_1:
            item[postfix] = getattr(self, f"get_{postfix}")(response.url)

        # func_postfix_list_2 = ["title", "price"]
        # for postfix in func_postfix_list_2:
        #     item[postfix] = getattr(self, f"get_{postfix}")(product_data)

        item["title"] = response.css('div.product_info_detail > h1::text').get().strip()

        price_int = response.css('div.product_detail_price::text').get().strip()[2:-1].replace(".", '')
        price_dec = response.css('div.product_detail_price > span::text').get("00").strip()
        item["price"] = round(float(f"{price_int}.{price_dec}"), 2)
        # print(item["price"])

        func_postfix_list_3 = [
            "product_id",
            # "title",
            "shipping_fee",
            # "price",
            "description",
            "rating",
            "reviews",
        ]
        for postfix in func_postfix_list_3:
            item[postfix] = getattr(self, f"get_{postfix}")(response)

        item["specifications"] = None
        item["brand"] = self.get_brand(response, item["product_id"])
        item["images"] = ";".join([img.replace('bestseller', 'original') for img in images])
        item["summary"] = f"{item['title']} {item['brand']}"
        item["videos"] = self.get_videos(response)

        cat_list = response.css('div.header_navigation > a::text').getall()[1:]
        print(cat_list)
        cat_list = [cat.strip() for cat in cat_list if cat.strip()]
        item["categories"] = " > ".join(cat_list) if cat_list else None
        # print(item["categories"])

        item["options"] = self.get_options(product_data)
        if item["options"] is None:
            item["variants"] = None
            item["has_only_default_variant"] = True
        else:
            item["variants"] = "something"
            item["has_only_default_variant"] = False

        preparation_days = self.get_preparation_days(response)

        if len(preparation_days) == 2:
            item["shipping_days_min"] = preparation_days[0]
            item["shipping_days_max"] = preparation_days[1]
        else:
            item["shipping_days_min"] = None
            item["shipping_days_max"] = None

        item["returnable"] = False

        item["available_qty"] = None
        item["description_en"] = None
        item["title_en"] = None
        item["upc"] = None
        item["sold_count"] = None
        item["weight"] = None
        item["width"] = None
        item["height"] = None
        item["length"] = None

        # print("*** item :", item)

        # just for check validation
        # product_to_upload = StandardProduct(**item)
        # json.dumps(product_to_upload.model_dump(mode='json'), ensure_ascii=False)

        yield item
