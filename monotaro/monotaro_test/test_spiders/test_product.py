import unittest

from scrapy.utils.test import get_crawler
from scrapy.http import HtmlResponse

from monotaro.spiders.product import MonotaroProduct


# python -m monotaro_test.test_spiders.test_product
class TestProduct(unittest.TestCase):
    def setUp(self):
        self.crawler = get_crawler(MonotaroProduct)
        self.spider = self.crawler._create_spider()

    def test_available_product_1(self):
        url = "https://www.monotaro.com/g/01429775/"
        with open("monotaro_test/pages/3579 A4ステーショナリーケース L型 和泉化成 クリア色 材質PP - 【通販モノタロウ】.html", "rb") as file:
            body = file.read()

        response = HtmlResponse(
            url=url,
            body=body,
        )
        result = list(self.spider.parse(response, 0, '01429775'))
        self.assertEqual(len(result), 1)
        product = result[0]

        target_product = {
            "url": url,
            "product_id": "01429775",
            "existence": True,
            "title": "A4ステーショナリーケース L型",
            "sku": "23197143",
            "brand": "和泉化成",
            "specifications": [
                {
                    "name": "サイズ",
                    "value": "A4"
                },
                {
                    "name": "色",
                    "value": "クリア"
                },
                {
                    "name": "寸法(mm)",
                    "value": "317×253×27"
                },
                {
                    "name": "内容量",
                    "value": "1個"
                }
            ],
            "categories": "オフィスサプライ > 事務用品 > ファイリング > 収納ボックス/ケース > 書類ケース",
            "images": "https://jp.images-monotaro.com/Monotaro3/pi/full/mono23197143-160331-02.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono23197143-210302-02.jpg",
            "price": 1.17,
            "available_qty": None,
            "options": [{
                "id": None,
                "name": "品番"
            }],
            "variants": [{
                "variant_id": "23197143",
                "barcode": None,
                "sku": "23197143",
                "option_values": [{
                    "option_id": None,
                    "option_value_id": None,
                    "option_name": "品番",
                    "option_value": "3579"
                }],
                "images": None,
                "price": 1.17,
                "available_qty": None
            }],
            "reviews": 15,
            "rating": 3.47,
            "shipping_fee": 3.26,
            "weight": None,
            "length": 12.48,
            "width": 9.96,
            "height": 1.06
        }
        for key in target_product:
            self.assertEqual(product[key], target_product[key])

        self.assertIn("<h4>注意</h4>", product["description"])
        self.assertIn("<th>材質</th>", product["description"])
        print(product["description"])

    def test_available_product_2(self):
        url = "https://www.monotaro.com/g/00530783/"
        with open("monotaro_test/pages/C-002F 携帯酸素 富士さん素 ルック 寸法Φ66×250mm 1本(5L) C-002F - 【通販モノタロウ】.html", "rb") as file:
            body = file.read()

        response = HtmlResponse(
            url=url,
            body=body,
        )
        result = list(self.spider.parse(response, 0, '00530783'))
        self.assertEqual(len(result), 1)
        product = result[0]

        target_product = {
            "url": url,
            "product_id": "00530783",
            "existence": True,
            "title": "携帯酸素 富士さん素",
            "sku": "58154695",
            "brand": "ルック",
            "specifications": [
                {
                    "name": "寸法(mm)",
                    "value": "Φ66×250"
                },
                {
                    "name": "RoHS指令(10物質対応)",
                    "value": "対応"
                },
                {
                    "name": "内容量",
                    "value": "1本(5L)"
                }
            ],
            "categories": "医療・介護用品 > 救急・衛生 > 救急・救助用品 > 酸素スプレー・吸入器",
            "images": "https://jp.images-monotaro.com/Monotaro3/pi/full/mono58154695-130311-02.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono58154695-201127-02.jpg",
            "price": 5.61,
            "available_qty": None,
            "options": [{
                "id": None,
                "name": "品番"
            }],
            "variants": [{
                "variant_id": "58154695",
                "barcode": None,
                "sku": "58154695",
                "option_values": [{
                    "option_id": None,
                    "option_value_id": None,
                    "option_name": "品番",
                    "option_value": "C-002F"
                }],
                "images": None,
                "price": 5.61,
                "available_qty": None
            }],
            "reviews": 5,
            "rating": 3.80,
            "shipping_fee": 3.26,
            "weight": None,
            "length": 2.60,
            "width": 2.60,
            "height": 9.84
        }
        for key in target_product:
            self.assertEqual(product[key], target_product[key])

        self.assertIn("<h4>注意</h4>", product["description"])
        self.assertIn("<th>用途</th>", product["description"])
        print(product["description"])

    def test_unavailable_product(self):
        url = "https://www.monotaro.com/g/06431439/"
        with open("monotaro_test/pages/AP-708209 お医者さんの(R)首サポーター Fit 1個 アルファックス 【通販モノタロウ】.html", "rb") as file:
            body = file.read()

        response = HtmlResponse(
            url=url,
            body=body,
        )
        result = list(self.spider.parse(response, 0, '06431439'))
        self.assertEqual(len(result), 1)
        product = result[0]

        target_product = {
            "url": url,
            "product_id": "06431439",
            "existence": False,
            "title": "お医者さんの(R)首サポーター Fit",
            "sku": "61690687",
            "brand": "アルファックス",
            "specifications": [
                {
                    "name": "質量(g)",
                    "value": "100"
                },
                {
                    "name": "寸法(cm)",
                    "value": "縦8・横57.5・厚み1.7"
                },
                {
                    "name": "首廻り(cm)",
                    "value": "30～46"
                },
                {
                    "name": "内容量",
                    "value": "1個"
                }
            ],
            "categories": "医療・介護用品 > ヘルスケア > サポーター・テーピング > サポーター > 首用 サポーター",
            "images": "https://jp.images-monotaro.com/Monotaro3/pi/full/mono61690687-240311-02.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono61690687-240311-04.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono61690687-240311-06.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono61690687-240311-08.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono61690687-240311-10.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono61690687-240311-12.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono61690687-240311-14.jpg",
            "price": 24.79,
            "available_qty": 0,
            "options": [{
                "id": None,
                "name": "品番"
            }],
            "variants": [{
                "variant_id": "61690687",
                "barcode": None,
                "sku": "61690687",
                "option_values": [{
                    "option_id": None,
                    "option_value_id": None,
                    "option_name": "品番",
                    "option_value": "AP-708209"
                }],
                "images": None,
                "price": 24.79,
                "available_qty": 0
            }],
            "reviews": None,
            "rating": None,
            "shipping_fee": 0.00,
            "weight": 0.22,
            "length": None,
            "width": None,
            "height": None,
        }
        for key in target_product:
            self.assertEqual(product[key], target_product[key])

        self.assertNotIn("<h4>注意</h4>", product["description"])
        self.assertIn("<th>用途</th>", product["description"])
        self.assertIn("<th>材質</th>", product["description"])
        print(product["description"])


if __name__ == '__main__':
    unittest.main()
