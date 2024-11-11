# 使用上级目录中的utils
import sys
sys.path.append('..')

import json
import re
from datetime import datetime
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
import scrapy
from scrapy.http import HtmlResponse
import scrapy.selector


# scrapy crawl product
class ProductSpider(scrapy.Spider):
    name = "product"
    allowed_domains = ["apodiscounter.de"]
    start_urls = []

    EXCHANGE_RATE_EUR_TO_US = 1.1024

    custom_settings = {
        "ITEM_PIPELINES": {
            "utils.mongodb.pipeline1.MongoPipeLine1": 400,
        }
    }

    COOKIES = {
        "_pin_unauth": "dWlkPU5UZ3dZemN5TmpJdFlXWmhNeTAwT1RrM0xUZ3labVV0Tm1RNU9EZ3daalJsWlRoaw",
        "_dy_toffset": "0",
        "_dycnst": "dg",
        "_dy_lu_ses": "d4ab8c441588ecbd81c621b16d1bc380%3A1730927477936",
        "XTCsid": "d89efafd889bf6f7e1975dbe6af335bd",
        "_dyid_server": "7921831999678700014",
        "_banner_above_shown": "shown",
        "_dy_test_02": "096",
        "_dycst": "dk.w.c.ws.fst.",
        "_sn_m": "{\"r\":{\"n\":1,\"r\":\"apodiscounter\"}}",
        "_uetvid": "c1450dc09c8211efaba6eb635a4b8807",
        "_pk_ses.4.be2b": "1",
        "_sn_n": "{\"cs\":{\"2330\":{\"t\":{\"i\":1,\"c\":\"2330cf61-ecbf-40f2-9759-61b9a2d46f9e2,1,6,20\"},\"i\":[1762463096769,1],\"c\":1,\"h\":1},\"7e1c\":{\"t\":{\"i\":1,\"c\":\"7e1c0f36-d706-44da-a27e-96153d652e7f4,2,35,20\"},\"i\":[1762463478167,0]},\"d43b\":{\"t\":{\"i\":1,\"c\":\"d43b9df3-2b85-4dab-a4f1-4475adbcc7424,2,35,20\"},\"i\":[1762463478168,0]}},\"a\":{\"i\":\"71c7debd-8f2a-4951-9a8c-584667ee2738\"},\"ssc\":1}",
        "_dy_soct": "1730927478!764678.-392'764686.-1'802509.0'860926.-1'889625.-392'943385.-392'943404.-1'1121737.-1'1275663.-392'1309941.-1!",
        "_ga_FHXN0W96Y4": "GS1.1.1730927087.1.1.1730927477.58.0.0",
        "_ga": "GA1.1.284978151.1730927087",
        "_pk_id.4.be2b": "a009a9652dcda963.1730927087.",
        "_pk_id.271.be2b": "86ea0ac351259201.1730927088.1.1730927478.1730927088.",
        "_dycs_overlay-recs": "5",
        "baqend-speedkit-user-id": "6HimcfaE2KdszhHWewoOBkF3o",
        "_dy_csc_ses": "t",
        "_dy_df_geo": "United%20States.Missouri.Saint%20Ann",
        "_dy_geo": "US.NA.US_MO.US_MO_Saint%20Ann",
        "_dy_ses_load_seq": "85690%3A1730927477669",
        "_dyid": "7921831999678700014",
        "_dyjsession": "d4ab8c441588ecbd81c621b16d1bc380",
        "_fbp": "fb.1.1730927087440.89770273643273802",
        "_gcl_au": "1.1.1261121574.1730927087",
        "_pk_ses.271.be2b": "1",
        "_sn_a": "{\"a\":{\"s\":1730927087660,\"l\":\"https://www.apodiscounter.de/\"},\"v\":\"b8fa0c41-0897-4ff2-9be6-f26742f2750d\",\"g\":{\"sc\":{\"2330cf61-ecbf-40f2-9759-61b9a2d46f9e\":1}}}",
        "_uetsid": "c144e6009c8211efb4120fbec52d5261",
        "baqend-speedkit-config": "%7B%22group%22%3A%22B%22%2C%22testId%22%3A%2250vs50_2024_09_02%22%7D",
        "c_controller_118_122": "1",
        "CSS_STATUS": "is_loaded",
        "desiredTemplate": "desktop",
        "dy_fs_page": "www.apodiscounter.de",
        "ksid": "UpMQnfVebEc0SNZTyDLhedsW",
        "lantern": "c3e70da4-4241-44d6-8c6c-58a500a90d3f",
        "SNS": "1",
        "cf_clearance": "HzhHvTI2UTwAeAftMSVeSgzpGzRf2IwjZilHvss73Q0-1730929198-1.2.1.1-cOyax8tLYJINLSQU5FAmOAF0sRs27pbGMNqOD7__Hlj7V0QcdsCViA9yeZyL.JbUWi1UEsRcCwJevYTROFHWvDXjWrI67PRe03I4gA032LqVsyiMcXUAwsm5pgAaUc0wlOsx1F3F99czuTIUQw2VwLjqAl6ZGJy0ELS6HCuZlyPRV58u6Xp58iVQTVGB_a0Gzs8DhEECbRHiKA51i3t6aUxZ6tzqafesyZ_XqewmCeEY4rDNS9MxfD5fThC7BTMBg8RhryGcJ1QiBR8YjkahQeMsW65CfuejFaBICe3tQ_2wR8dKzxCIqTB.N.rFm5kFJdekthCeS1KYy99eIoASMnFAriAPhLQ0zdIksa5WqopbDmIjAChs6vIlLrzY_Te1eUhYkDoGX8lXZVXzFYHeIzwFd_z2DcvdIn0p4Ku_AqW0g4myiP8LMAwy.BnIPWsruJpjZ.Bl8mQdNydZ26rmpg"
    }

    HEADERS = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
        "Accept-Language": "de-DE,de;q=0.8,en-GB;q=0.5,en;q=0.3",
        "Referer": "https://www.google.de",
        "Sec-Ch-Ua-Platform": "\"Windows\"",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0"
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        with open('apodiscounter_produkturls.json', 'r') as f:
            produits = json.load(f)
        self.start_urls = [p['prod_url'] for p in produits]
        print(f'Insgesamt {len(self.start_urls):_} Produkt(e)'.replace("_", "."))

    def start_requests(self):
        for i, url in enumerate(self.start_urls):
            print(f"{i+1:_}/{len(self.start_urls)}", url)

            yield scrapy.Request(url,
                meta={ "cookiejar": i },
                headers=self.HEADERS,
                cookies=self.COOKIES,
                callback=self.parse,
                errback=self.errback,
            )

    def get_product_data(self, response: HtmlResponse):
        product_data = None
        script_list = response.xpath("//script[@type='application/ld+json']/text()").getall()

        for script in script_list:
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
        if not product_data:
            print("")
            return None
        return product_data["name"]

    def get_price(self, product_data: dict):
        f_price_us = None
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

        for tag in tags:
            description += tag.replace('\n', '').replace('\r', '').replace('\xa0', '&nbsp;')

        description += '</div>'
        return description

    def get_videos(self, response: HtmlResponse):
        """
        获得商品影片（从选择器"div#gallery_products_video"判断最多只有一个）
        """

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
        if not tag:
            return days

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
        self.logger.info(f"{response.url}: {response.status}")
        if response.status > 300:
            return
        images = response.css('div.product_image_50_50 > img::attr(src)').getall()
        if not images:
            print("Produkt ohne Bilder ignoriert")
            return

        product_data = self.get_product_data(response) # 这个JSON有时会读不到？

        item = {}

        item["url"] = response.url
        item["date"] = datetime.now().replace(microsecond=0).isoformat()
        item["existence"] = False if response.status == 200 else False

        func_postfix_list_1 = ["sku", "source"]
        for postfix in func_postfix_list_1:
            item[postfix] = getattr(self, f"get_{postfix}")(response.url)

        item["title"] = response.css('div.product_info_detail > h1::text').get().strip()

        price_int = response.css('div.product_detail_price::text').get().strip()[2:-1].replace(".", '')
        price_dec = response.css('div.product_detail_price > span::text').get("00").strip()
        item["price"] = round(float(f"{price_int}.{price_dec}"), 2)

        func_postfix_list_3 = [
            "product_id",
            "shipping_fee",
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
        cat_list = [cat.strip() for cat in cat_list if cat.strip()]
        item["categories"] = " > ".join(cat_list) if cat_list else None

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

        yield item
