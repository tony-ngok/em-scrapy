from datetime import datetime
import json
import re
import os
import scrapy
import scrapy.selector
# from apodiscounter.items import ProductItem
# from apodiscounter.product_manager.formatter import get_product

# from urllib.parse import urlparse, urlunparse
# from resources.base_spider import BaseSpider

from em_product.product import StandardProduct
from bs4 import BeautifulSoup


class ProductSpider(BaseSpider):
    name = "product"
    allowed_domains = ["apodiscounter.de"]
    start_urls = []

    EXCHANGE_RATE_EUR_TO_US = 1.11

    custom_settings = {
        "ITEM_PIPELINES": {
            "apodiscounter.pipelines.ProductPipeline": 400,
        }
    }

    def __init__(self, *args, **kwargs):
        super(ProductSpider, self).__init__(*args, **kwargs)
        self.cookies = {
            "XTCsid": "8e6fd8f24f5e249042fcd3f657bdabc5",
            "desiredTemplate": "desktop",
            "baqend-speedkit-user-id": "l8qoiCQIpG62nyBNRLXcuxw4z",
            "ksid": "Q5moqCIWM9aqopKybRyDIUyw",
            "_dy_csc_ses": "t",
            "_gcl_au": "1.1.732181847.1724341915",
            "_dycnst": "dg",
            "_dyid": "-7647111912147689830",
            "_dy_geo": "US.NA.US_MO.US_MO_Saint%20Ann",
            "_dy_df_geo": "United%20States.Missouri.Saint%20Ann",
            "_dy_toffset": "0",
            "c_controller_118_122": "1",
            "_dycs_overlay-recs": "5",
            "_dy_test_02": "096",
            "_ga": "GA1.1.308076624.1724341915",
            "_pin_unauth": "dWlkPU1ESTVPV00yTmpNdFpESXpZaTAwT0RrNUxXSTVaREF0WkRFMU1ERXlNVEl4TW1VeA",
            "SNS": "1",
            "_pk_id.4.be2b": "96b811db45fb5ce6.1724341915.",
            "sanofiBottombar": "1",
            "CSS_STATUS": "is_loaded",
            "_ALGOLIA": "anonymous-1862bc10-c7db-4584-abf6-724f6ac137dc",
            "_pk_ses.271.be2b": "1",
            "_pk_ses.4.be2b": "1",
            "_dycst": "dk.l.c.ms.",
            "dy108": "aws",
            "_sn_n": '{"a":{"i":"42f76ca5-011b-46a0-91b7-b9d2c74422af"}}',
            "_dyid_server": "-7647111912147689830",
            "cf_clearance": "1Nthvbe0zy1odS2A7b7fX2qcEwEExIrOZ51EnxA6Amo-1724372104-1.2.1.1-KCSjeYihoYThBT445IrUqGPWmz.oLXfp4AyIfRZcfitUuNfzBaeuDdfD2dnZREuKGE34rPmRoE7.XyftoyioPg4DXumJNEcE1z9cZ2JjWXxnSqerJxAIA8MAMbC4ITNSqtSN1JX8QlTYDcFfBAfpKup8gfDYWLyf285mhC3ZNE8n4pLgwt_LTEleddjN0p3Zb22dTbW8cRBG81vAk6CmhbNFy9sc.DLW7MzRvsNMaNb_VeC1suggvgR7Y6LzHHpuKv8c4dtd3Mkw0XRXdKJIfE8j3Qc2pTyfkL3cr0hlooOunQ_RTp.jn4Xjd9oMitKHyNEgmRzNUcZZZOhkmV8vDTX63kxbjhQnFrjpXHa3tYbA7SPTrcujqYvcLptLgQd9",
            "source": "35.192.187.156",
            "_pk_id.271.be2b": "35005e5edeaea056.1724341915.2.1724372108.1724371511.",
            "_uetsid": "748f9680609e11efb27c4dbf3566c48e",
            "_uetvid": "748f9d00609e11ef8bced9d01bb3d0ef",
            "_dy_ses_load_seq": "99917%3A1724372108390",
            "_ga_FHXN0W96Y4": "GS1.1.1724371511.3.1.1724372108.60.0.0",
            "_dy_lu_ses": "e2c59da4490a8f0a2e25c09f5e2193ad%3A1724372108507",
            "_dy_soct": "1724372108!764678.-597'764686.0'802509.-338'860926.0'889625.-597'943385.-30194'943387.-597'943404.0'985911.0'1000393.0'1121737.-30194'1252335.-595'1275663.-597'1309941.0'1361036.-597'2223932.-29729'2223934.-338'2324273.-592!",
            "_sn_m": '{"r":{"n":1,"r":"35.192.187"}}',
            "_sn_a": '{"a":{"s":1724371512121,"l":"https://www.apodiscounter.de/stero-enurex-klingelhose-groesse-0-1stk-pzn-06914103","e":1724371512120},"v":"fe8cb026-c5ea-4974-98da-d5f287b7f55c"}',
        }

    def start_requests(self):
        for url in ProductSpider.start_urls:
            yield scrapy.Request(
                url,
                method="GET",
                headers=self.get_headers(),
                # cookies=self.cookies,
                errback=self.errback,
            )

    def get_product_data(self, response):
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

    def get_global_product_data(self, response):
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

    def get_product_id(self, response):
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

    def get_title(self, response):
        product_data = self.get_product_data(response)
        if not product_data:
            return None
        return product_data["name"]

    def get_price(self, response):
        f_price_us = None
        f_value = float(self.get_product_data(response)["offers"]["price"])

        f_price_us = round(f_value * self.EXCHANGE_RATE_EUR_TO_US, 2)
        return f_price_us

    def get_shipping_fee(self, response):
        shipping_fee = None

        shipping_cost_text = response.xpath(
            "//div[@class='product_info_shipping_costs_information']/text()"
        ).get()

        if "Gratis" in shipping_cost_text and "Versand" in shipping_cost_text:
            shipping_fee = 0

        return shipping_fee

    def get_description(self, response):
        description = None

        tag = response.xpath("//div[@id='products_description_manufacturer']").get()
        soup = BeautifulSoup(tag, "html.parser")
        div = soup.find("div")

        description = div.text.strip()
        return description

    def get_images(self, response, product_id):
        str_images = ""
        global_data = self.get_global_product_data(response)
        str_images = global_data[product_id]["src"]["image_size_original"].replace("\\", "")

        to_replace = "https://www.apodiscounter.de/https://www.apodiscounter.de"
        if to_replace in str_images:
            str_images = str_images.replace(to_replace, "https://www.apodiscounter.de")

        # print("str_images = ", str_images)

        return str_images

    def get_videos(self, response):
        videos = None

        if "youtube" in response.text.lower() or ".mp4" in response.text.lower():
            print("THERE IS VIDEO, NEED TO MAKE CODE FOR PARSE VIDEO\n")
            breakpoint()

        return videos

    def get_options(self, response):
        options = None

        product_data = self.get_product_data(response)

        if type(product_data["offers"]) is type(list()):
            print("THERE ARE MULTIPLE OFFERS, NEED PARSE CODE FOR OPTIONS")
            breakpoint()
        elif type(product_data["offers"]) is type(dict()):
            options = None

        return options

    def get_rating(self, response):
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

    def get_reviews(self, response):
        reviews = None

        tag = response.xpath("//div[@id='product_description_tab_3']").get()

        soup = BeautifulSoup(tag, "html.parser")
        divs = soup.find_all("div")

        text = ""
        for div in divs:
            text += div.text.strip()
        if "(" in text and "}" in text:
            values = re.findall(r"[-+]?(?:\d*)", text)
            rets = []
            for x in values:
                if x.isdigit():
                    rets.append(int(x))
            if len(rets) == 1:
                reviews = rets[0]

        return reviews

    def get_preparation_days(self, response):
        days = []
        tag = response.xpath(
            "//div[@class='product_info_shipping_information']//div[@class='product_status_box']/span[@class='product_status_link']"
        ).get()
        soup = BeautifulSoup(tag, "html.parser")
        first_span = soup.find("span")

        text_all = ""
        # print("span text : ", first_span.text.strip())
        text_all += first_span.text.strip()

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
            else:
                print("PARSE SHIPPING DAYS, ENCOUNTER EXCEPTION, NEED CHECK")
                breakpoint()

        return days

    def get_headers(self):
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "en-US,en;q=0.9",
            "priority": "u=0, i",
            "sec-ch-ua": '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Linux"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
        }

        return headers

    def errback(self, failure):
        self.logger.error(f"{failure.request.url}: {repr(failure)}")

    def parse(self, response):
        self.logger.info(f"{response.url}: {response.status}")
        if response.status > 300:
            return None
        item = get_product(response)

        item["url"] = response.url
        item["date"] = datetime.now().replace(microsecond=0).isoformat()
        item["existence"] = True if response.status == 200 else False

        func_postfix_list_1 = ["sku", "source"]
        for postfix in func_postfix_list_1:
            item[postfix] = getattr(self, f"get_{postfix}")(response.url)

        func_postfix_list_2 = [
            "product_id",
            "title",
            "shipping_fee",
            "price",
            "description",
            "rating",
            "reviews",
        ]
        for postfix in func_postfix_list_2:
            item[postfix] = getattr(self, f"get_{postfix}")(response)

        item["specifications"] = None
        item["brand"] = self.get_brand(response, item["product_id"])
        item["images"] = self.get_images(response, item["product_id"])

        item["summary"] = f"{item['title']} {item['brand']}"

        item["videos"] = self.get_videos(response)

        item["options"] = self.get_options(response)
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
