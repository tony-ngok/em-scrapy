import unittest

from scrapy.utils.test import get_crawler
from scrapy.http import HtmlResponse

from australianorganicproducts.spiders.product import AopProduct


# python -m australianorganicproducts_test.test_spiders.test_product
class TestProduct(unittest.TestCase):
    def setUp(self):
        self.crawler = get_crawler(AopProduct)
        self.spider = self.crawler._create_spider()

    def test_available_product_1(self):
        url = "https://australianorganicproducts.com.au/collections/vegetarian/products/clover-fields-australian-lavender-soap-single-bar"
        with open("australianorganicproducts_test/pages/CLOVER FIELDS Australian Lavender Soap Single Bar — Australian Organic Products.html", "rb") as file:
            body = file.read()

        response = HtmlResponse(
            url=url,
            body=body,
        )
        result = list(self.spider.parse(response))
        self.assertEqual(len(result), 1)
        product = result[0]
        print(product["description"])

        target_product = {
            "url": url,
            "product_id": "8536864948447",
            "existence": True,
            "title": "CLOVER FIELDS Australian Lavender Soap Single Bar",
            "sku": "CVALS-OB",
            "upc": None,
            "brand": "Clover Fields",
            "categories": "Vegetarian",
            "images": "https://australianorganicproducts.com.au/cdn/shop/files/Clover_Fields_Australian_Lavender_Soap_100g_media-01_a7d48828-4690-4079-8133-ef75d349789c_1200x1200.jpg",
            "price": 1.62,
            "available_qty": 1,
            "options": None,
            "variants": None,
            "reviews": None,
            "rating": None,
            "shipping_fee": 6.60,
            "weight": 0.26
        }
        for key in target_product:
            self.assertEqual(product[key], target_product[key])

        self.assertNotIn("Why buy from us?" , product["description"])
        self.assertNotIn("on sale!", product["description"])
        self.assertNotIn("</a>" , product["description"])

    def test_available_product_2(self):
        url = "https://australianorganicproducts.com.au/collections/vegan-products/products/lakewood-organic-pomegranate-blend-cold-pressed-946ml"
        with open("australianorganicproducts_test/pages/LAKEWOOD Organic Pomegranate Blend Fresh Pressed 946mL — Australian Organic Products.html", "rb") as file:
            body = file.read()

        response = HtmlResponse(
            url=url,
            body=body,
        )
        result = list(self.spider.parse(response))
        self.assertEqual(len(result), 1)
        product = result[0]

        target_product = {
            "url": url,
            "product_id": "9093955009",
            "existence": True,
            "title": "LAKEWOOD Organic Pomegranate Blend Fresh Pressed 946mL",
            "sku": "66759K",
            "upc": "042608470199",
            "brand": "Lakewood",
            "categories": "Vegan Products",
            "images": "https://australianorganicproducts.com.au/cdn/shop/products/Lakewood-Pom-Blend_400x400.jpg",
            "price": 11.34,
            "available_qty": 5,
            "options": None,
            "variants": None,
            "reviews": None,
            "rating": None,
            "shipping_fee": 6.60,
            "weight": 3.53
        }
        for key in target_product:
            self.assertEqual(product[key], target_product[key])

        self.assertNotIn("Why buy from us?" , product["description"])
        self.assertNotIn("on sale!", product["description"])
        self.assertNotIn("</a>" , product["description"])

    def test_unavailable_product(self):
        url = "https://australianorganicproducts.com.au/collections/vegan-products/products/clipper-organic-white-tea-26-tbags"
        with open("australianorganicproducts_test/pages/CLIPPER Organic White Tea 20 tbags — Australian Organic Products.html", "rb") as file:
            body = file.read()

        response = HtmlResponse(
            url=url,
            body=body,
        )
        result = list(self.spider.parse(response))
        self.assertEqual(len(result), 1)
        product = result[0]

        target_product = {
            "url": url,
            "product_id": "9087506113",
            "existence": False,
            "title": "CLIPPER Organic White Tea 20 tbags",
            "sku": "CLIP107-GBL",
            "upc": "5021991941801",
            "brand": "Clipper",
            "categories": "Vegan Products",
            "images": "https://australianorganicproducts.com.au/cdn/shop/products/26-White-Tea-NEW_590x_6b9eeda5-4f19-4174-a675-5a4c15b9eb4b_1000x1000.jpg",
            "price": 4.77,
            "available_qty": 0,
            "options": None,
            "variants": None,
            "reviews": None,
            "rating": None,
            "shipping_fee": 6.60,
            "weight": 0.18
        }
        for key in target_product:
            self.assertEqual(product[key], target_product[key])

        self.assertNotIn("Why buy from us?" , product["description"])
        self.assertNotIn("on sale!", product["description"])
        self.assertNotIn("</a>" , product["description"])

    def test_one_variant_product(self):
        url = "https://australianorganicproducts.com.au/collections/dairy-free/products/clover-fields-loofah-scrub-soap"
        with open("australianorganicproducts_test/pages/Clover Fields Loofah Scrub Soap — Australian Organic Products.html", "rb") as file:
            body = file.read()

        response = HtmlResponse(
            url=url,
            body=body,
        )
        result = list(self.spider.parse(response))
        self.assertEqual(len(result), 1)
        product = result[0]

        target_product = {
            "url": url,
            "product_id": "3757876379728",
            "existence": True,
            "title": "Clover Fields Loofah Scrub Soap",
            "sku": "CVLSS-OB",
            "upc": "3999000000134",
            "brand": "Clover Fields",
            "categories": "Dairy Free",
            "images": "https://australianorganicproducts.com.au/cdn/shop/products/Clover_Fields_Loofah_Scrub_Soap_100g_media-01_1200x1200.jpg",
            "price": 1.62,
            "available_qty": 32,
            "options": [{
                "id": None,
                "name": "Quantity"
            }],
            "variants": [{
                "variant_id": "29269751660624",
                "barcode": "3999000000134",
                "sku": "CVLSS-OB",
                "option_values": [{
                    "option_id": None,
                    "option_value_id": None,
                    "option_name": "Quantity",
                    "option_value": "Single bar"
                }],
                "images": "https://australianorganicproducts.com.au/cdn/shop/products/Clover_Fields_Loofah_Scrub_Soap_100g_media-01.jpg",
                "price": 1.62,
                "available_qty": 32
            }],
            "reviews": None,
            "rating": None,
            "shipping_fee": 6.60,
            "weight": 0.26
        }
        for key in target_product:
            self.assertEqual(product[key], target_product[key])

        self.assertNotIn("Why buy from us?" , product["description"])
        self.assertNotIn("on sale!", product["description"])
        self.assertNotIn("</a>" , product["description"])

    def test_multi_variant_product(self):
        url = "https://australianorganicproducts.com.au/collections/pet-care/products/biopet-adult-dog-food-grain-free"
        with open("australianorganicproducts_test/pages/BIOpet Adult Dog Food Grain Free — Australian Organic Products.html", "rb") as file:
            body = file.read()

        response = HtmlResponse(
            url=url,
            body=body,
        )
        result = list(self.spider.parse(response))
        self.assertEqual(len(result), 1)
        product = result[0]

        target_product = {
            "url": url,
            "product_id": "3678523293776",
            "existence": True,
            "title": "BIOpet Adult Dog Food Grain Free",
            "sku": "BAGFDF3.5kg-KO",
            "upc": "9328606000912",
            "brand": "Biopet",
            "categories": "Pet Care",
            "images": "https://australianorganicproducts.com.au/cdn/shop/products/BIOpet_Adult_Dog_Food_Grain_Free_800x800.jpg",
            "price": 32.16,
            "available_qty": 96,
            "options": [{
                "id": None,
                "name": "Size"
            }],
            "variants": [
                {
                    "variant_id": "28802786099280",
                    "barcode": "9328606000912",
                    "sku": "BAGFDF3.5kg-KO",
                    "option_values": [{
                        "option_id": None,
                        "option_value_id": None,
                        "option_name": "Quantity",
                        "option_value": "3.5kg"
                    }],
                    "images": "https://australianorganicproducts.com.au/cdn/shop/products/BIOpet_Adult_Dog_Food_Grain_Free.jpg",
                    "price": 32.16,
                    "available_qty": 96
                },
                {
                    "variant_id": "44411048362207",
                    "barcode": None,
                    "sku": "44411048362207",
                    "option_values": [{
                        "option_id": None,
                        "option_value_id": None,
                        "option_name": "Quantity",
                        "option_value": "13.5kg"
                    }],
                    "images": None,
                    "price": 75.60,
                    "available_qty": 94
                }
            ],
            "reviews": 1,
            "rating": 5.00,
            "shipping_fee": 6.60,
            "weight": 8.16
        }
        for key in target_product:
            self.assertEqual(product[key], target_product[key])

        self.assertNotIn("Why buy from us?" , product["description"])
        self.assertNotIn("on sale!", product["description"])
        self.assertNotIn("</a>" , product["description"])


if __name__ == '__main__':
    unittest.main()
