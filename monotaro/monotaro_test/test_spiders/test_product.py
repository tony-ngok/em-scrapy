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
            "videos": None,
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

        print(product["description"])
        self.assertIn("<h4>注意</h4>", product["description"])
        self.assertIn("<th>材質</th>", product["description"])

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
            "videos": None,
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

        print(product["description"])
        self.assertIn("<h4>注意</h4>", product["description"])
        self.assertIn("<th>用途</th>", product["description"])
    
    def test_available_product_3(self):
        url = "https://www.monotaro.com/g/06199072/"
        with open("monotaro_test/pages/JS8801 酸素濃度計 MCP=Joman 検知ガス酸素(O2) - 【通販モノタロウ】.html", "rb") as file:
            body = file.read()

        response = HtmlResponse(
            url=url,
            body=body,
        )
        result = list(self.spider.parse(response, 0, '06199072'))
        self.assertEqual(len(result), 1)
        product = result[0]

        target_product = {
            "url": url,
            "product_id": "06199072",
            "existence": True,
            "title": "酸素濃度計",
            "sku": "44631495",
            "brand": "MCP=Joman",
            "specifications": [
                {
                    "name": "寸法(mm)",
                    "value": "95.9×66.9×52"
                },
                {
                    "name": "測定範囲",
                    "value": "0～30%VOL"
                },
                {
                    "name": "質量(g)",
                    "value": "147.5(バッテリー含む)"
                },
                {
                    "name": "バッテリー",
                    "value": "3.7V 750mAh充電式リチウム電池"
                },
                {
                    "name": "解像度",
                    "value": "0.001"
                },
                {
                    "name": "警報方式",
                    "value": "ブザー音/フラッシュ/振動(高値と低値の設定が可能)"
                },
                {
                    "name": "動作温度(℃)",
                    "value": "‐10～50"
                },
                {
                    "name": "検知ガス",
                    "value": "酸素(O2)"
                },
                {
                    "name": "保管温度(℃)",
                    "value": "0～40"
                },
                {
                    "name": "バッテリー稼動時間",
                    "value": "60時間(作業により異なる場合あり)"
                },
                {
                    "name": "バックライト",
                    "value": "有り"
                },
                {
                    "name": "充電端子",
                    "value": "micro USB充電ポート"
                },
                {
                    "name": "内容量",
                    "value": "1個"
                }
            ],
            "categories": "測定・測量用品 > 測定用品 > 環境測定(自然環境/安全環境) > 酸素濃度計",
            "images": "https://jp.images-monotaro.com/Monotaro3/pi/full/mono44631495-230815-02.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono44631495-230815-04.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono44631495-230815-06.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono44631495-240318-04.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono44631495-240318-06.jpg",
            "videos": None,
            "price": 176.07,
            "available_qty": None,
            "options": [{
                "id": None,
                "name": "品番"
            }],
            "variants": [{
                "variant_id": "44631495",
                "barcode": None,
                "sku": "44631495",
                "option_values": [{
                    "option_id": None,
                    "option_value_id": None,
                    "option_name": "品番",
                    "option_value": "JS8801"
                }],
                "images": None,
                "price": 176.07,
                "available_qty": None
            }],
            "reviews": None,
            "rating": None,
            "shipping_fee": 0.00,
            "weight": 0.33,
            "length": 3.78,
            "width": 2.63,
            "height": 2.05
        }
        for key in target_product:
            self.assertEqual(product[key], target_product[key])

        print(product["description"])
        self.assertNotIn("<h4>注意</h4>", product["description"])
        self.assertIn("<th>機能</th>", product["description"])

    def test_available_product_4(self):
        url = "https://www.monotaro.com/g/06201561/"
        with open("monotaro_test/pages/アサヒ おいしい水 天然水 六甲 PET2L 1ケース(2L×6本) アサヒ飲料 【通販モノタロウ】.html", "rb") as file:
            body = file.read()

        response = HtmlResponse(
            url=url,
            body=body,
        )
        result = list(self.spider.parse(response, 0, '06201561'))
        self.assertEqual(len(result), 1)
        product = result[0]

        target_product = {
            "url": url,
            "product_id": "06201561",
            "existence": True,
            "title": "アサヒ おいしい水 天然水 六甲 PET2L",
            "sku": "44705756",
            "brand": "アサヒ飲料",
            "specifications": [
                {
                    "name": "寸法(mm)",
                    "value": "104×89.4×311"
                },
                {
                    "name": "質量(g)",
                    "value": "2029"
                },
                {
                    "name": "賞味期限",
                    "value": "720日"
                },
                {
                    "name": "原材料",
                    "value": "水(深井戸水)"
                },
                {
                    "name": "アレルギー",
                    "value": "なし"
                },
                {
                    "name": "内容量",
                    "value": "1ケース(2L×6本)"
                }
            ],
            "categories": "オフィスサプライ > 食品・飲料 > 水/ミネラルウォーター > ミネラルウォーター",
            "images": "https://jp.images-monotaro.com/Monotaro3/pi/full/mono44705756-230822-02.jpg",
            "videos": None,
            "price": 6.19,
            "available_qty": None,
            "options": None,
            "variants": None,
            "reviews": 4,
            "rating": 4.50,
            "shipping_fee": 3.26,
            "weight": 4.47,
            "length": 4.09,
            "width": 3.52,
            "height": 12.24
        }
        for key in target_product:
            self.assertEqual(product[key], target_product[key])

        print(product["description"])
        self.assertNotIn("<h4>注意</h4>", product["description"])
        self.assertIn("<th>栄養成分</th>", product["description"])

    def test_available_product_5(self):
        url = "https://www.monotaro.com/g/02362145/"
        with open("monotaro_test/pages/クリアホルダー 厚さ0.2mm モノタロウ クリヤーホルダー 【通販モノタロウ】.html", "rb") as file:
            body = file.read()

        response = HtmlResponse(
            url=url,
            body=body,
        )
        result = list(self.spider.parse(response, 0, '02362145'))
        self.assertEqual(len(result), 1)
        product = result[0]

        target_product = {
            "url": url,
            "product_id": "02362145",
            "existence": True,
            "title": "クリアホルダー 厚さ0.2mm",
            "sku": "48713035",
            "brand": "モノタロウ",
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
                    "name": "厚さ(mm)",
                    "value": "0.2"
                },
                {
                    "name": "寸法(mm)",
                    "value": "308×219"
                }
            ],
            "categories": "オフィスサプライ > 事務用品 > ファイリング > クリヤーホルダー",
            "images": "https://jp.images-monotaro.com/Monotaro3/pi/full/mono48713044-221004-01.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono48713035-170706-04.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono48713035-221004-02.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono54841650-240612-02.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono54841650-240612-06.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono54841650-240614-02.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono54841659-240612-02.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono54841659-240614-02.jpg",
            "videos": "https://www.youtube.com/embed/U9V_QlSnrik",
            "price": 0.84,
            "available_qty": None,
            "options": [
                {
                    "id": None,
                    "name": "品番"
                },
                {
                    "id": None,
                    "name": "内容量"
                }
            ],
            "variants": [
                {
                    "variant_id": "48713035",
                    "barcode": None,
                    "sku": "48713035",
                    "option_values": [
                        {
                            "option_id": None,
                            "option_value_id": None,
                            "option_name": "品番",
                            "option_value": "MCH-02A410"
                        },
                        {
                            "option_id": None,
                            "option_value_id": None,
                            "option_name": "内容量",
                            "option_value": "1パック(10枚)"
                        }
                    ],
                    "images": "https://jp.images-monotaro.com/Monotaro3/pi/full/mono48713035-221004-02.jpg",
                    "price": 0.84,
                    "available_qty": None
                },
                {
                    "variant_id": "54841650",
                    "barcode": None,
                    "sku": "54841650",
                    "option_values": [
                        {
                            "option_id": None,
                            "option_value_id": None,
                            "option_name": "品番",
                            "option_value": "MCH-02A4100"
                        },
                        {
                            "option_id": None,
                            "option_value_id": None,
                            "option_name": "内容量",
                            "option_value": "1パック(100枚)"
                        }
                    ],
                    "images": "https://jp.images-monotaro.com/Monotaro3/pi/full/mono54841650-240614-02.jpg",
                    "price": 7.77,
                    "available_qty": 0
                },
                {
                    "variant_id": "54841659",
                    "barcode": None,
                    "sku": "54841659",
                    "option_values": [
                        {
                            "option_id": None,
                            "option_value_id": None,
                            "option_name": "品番",
                            "option_value": "MCH-02A4600"
                        },
                        {
                            "option_id": None,
                            "option_value_id": None,
                            "option_name": "内容量",
                            "option_value": "1箱(600枚)"
                        }
                    ],
                    "images": "https://jp.images-monotaro.com/Monotaro3/pi/full/mono54841659-240614-02.jpg",
                    "price": 43.66,
                    "available_qty": 0
                }
            ],
            "reviews": 438,
            "rating": 4.69,
            "shipping_fee": 3.26,
            "weight": None,
            "length": 12.13,
            "width": 8.62,
            "height": None
        }
        for key in target_product:
            self.assertEqual(product[key], target_product[key])

        print(product["description"])
        self.assertIn("<h4>注意</h4>", product["description"])
        self.assertIn("<th>用途</th>", product["description"])
        self.assertIn("<th>材質</th>", product["description"])

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
            "videos": None,
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

        print(product["description"])
        self.assertNotIn("<h4>注意</h4>", product["description"])
        self.assertIn("<th>用途</th>", product["description"])
        self.assertIn("<th>材質</th>", product["description"])


if __name__ == '__main__':
    unittest.main()
