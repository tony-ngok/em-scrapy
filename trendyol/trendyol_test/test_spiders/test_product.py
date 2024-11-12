import unittest

from em_product.product import StandardProduct
from scrapy.utils.test import get_crawler
from scrapy.http import HtmlResponse

from trendyol.spiders.produit import TrendyolProduit


# python -m trendyol_test.test_spiders.test_product
class TestProduct(unittest.TestCase):
    def setUp(self):
        self.crawler = get_crawler(TrendyolProduit)
        self.spider = self.crawler._create_spider()

    def test_available_product_1(self):
        url = "https://www.trendyol.com/bioderma/sebium-foaming-gel-500-ml-p-132469"
        with open("trendyol_test/pages/Bioderma Sébium Foaming Gel Yüz Yıkama Jeli 500 ml Yorumları, Fiyatı - Trendyol.html", "rb") as file:
            body = file.read()
        resp1 = HtmlResponse(
            url=url,
            body=body,
        )
        res1 = list(self.spider.parse(resp1))
        self.assertEqual(len(res1), 1)
        prod1 = res1[0]["item"]

        has_more_descr = res1[0]["has_more_descr"]
        video_id = res1[0]["video_id"]
        self.assertTrue(has_more_descr)
        self.assertIsNone(video_id)

        url2 = "https://apigw.trendyol.com/discovery-web-productgw-service/api/product-detail/132469/html-content?channelId=1"
        with open("trendyol_test/pages/132469.json", "rb") as file2:
            body2 = file2.read()
        response = HtmlResponse(
            url=url2,
            body=body2
        )
        result = list(self.spider.parse_descr_page(response, prod1, video_id))
        self.assertEqual(len(result), 1)
        product = result[0]

        target_product = {
            "url": url,
            "product_id": "132469",
            "existence": True,
            "title": "Sebium Foaming Gel 500 ml",
            "sku": "132469",
            "upc": "3401399277092",
            "brand": "Bioderma",
            "specifications": [
                {
                    "name": "Cilt Tipi",
                    "value": "Karma"
                },
                {
                    "name": "Form",
                    "value": "Jel"
                },
                {
                    "name": "Kullanma Amacı",
                    "value": "Nemlendirici"
                },
                {
                    "name": "Ek Özellik",
                    "value": "Anti Alerjik"
                },
                {
                    "name": "Hacim",
                    "value": "500 ml"
                },
                {
                    "name": "İçerik",
                    "value": "E Vitamini"
                },
                {
                    "name": "Tip",
                    "value": "Şişe"
                },
                {
                    "name": "Menşei",
                    "value": "FR"
                }
            ],
            "categories": "Bioderma > Kozmetik > Cilt Bakımı > Yüz Bakım > Yüz Temizleyicileri",
            "images": "https://cdn.dsmcdn.com/ty1601/product/media/images/prod/PIM/20241111/07/836433cc-933e-4af6-99e9-bf50a436d3bd/1_org_zoom.jpg;https://cdn.dsmcdn.com/ty1599/product/media/images/prod/PIM/20241111/07/3816bdb7-5ee5-465e-a167-4e903c4937f1/1_org_zoom.jpg;https://cdn.dsmcdn.com/ty1599/product/media/images/prod/PIM/20241111/07/3e35d2ad-6a07-4e1d-888a-f93f4ca3e3ec/1_org_zoom.jpg;https://cdn.dsmcdn.com/ty1600/product/media/images/prod/PIM/20241111/07/d8c97c55-6262-4d30-96c0-1db5b79eb003/1_org_zoom.jpg;https://cdn.dsmcdn.com/ty1600/product/media/images/prod/PIM/20241111/07/2a550520-d74f-415b-9711-cfde0c47ad25/1_org_zoom.jpg;https://cdn.dsmcdn.com/ty1600/product/media/images/prod/PIM/20241111/07/086f5fcb-8935-4682-8244-7084f67522f2/1_org_zoom.jpg;https://cdn.dsmcdn.com/ty1600/product/media/images/prod/PIM/20241111/07/f3df1cb6-585d-4630-b906-d7a6b9314eea/1_org_zoom.jpg;https://cdn.dsmcdn.com/ty1600/product/media/images/prod/PIM/20241111/07/4871e252-e4cd-42ec-9903-e54e99564fcd/1_org_zoom.jpg",
            "videos": None,
            "price": 13.09,
            "available_qty": None,
            "options": None,
            "variants": None,
            "reviews": 26950,
            "rating": 4.58,
            "shipping_fee": 0.00,
            "weight": None,
            "length": None,
            "width": None,
            "height": None
        }
        for key in target_product:
            self.assertEqual(product[key], target_product[key])

        print(product["description"])
        StandardProduct(**prod1)

    # def test_available_product_2(self):
    #     url = "https://www.trendyol.com/copierbond/ve-ge-a4-fotokopi-kagidi-80-g-500-lu-5-paket-2500ad-1-koli-p-6026206"
    #     with open("trendyol_test/pages/Copier Bond A4 Kağıdı 80 g 5'li Paket 80 g 500 Yaprak 2500 Adet Fiyatı - Trendyol.html", "rb") as file:
    #         body = file.read()

    #     response = HtmlResponse(
    #         url=url,
    #         body=body,
    #     )
    #     result = list(self.spider.parse(response, 0))
    #     self.assertEqual(len(result), 1)
    #     product = result[0]

    #     target_product = {
    #         "url": url,
    #         "product_id": "01429775",
    #         "existence": True,
    #         "title": "A4ステーショナリーケース L型",
    #         "sku": "23197143",
    #         "brand": "和泉化成",
    #         "specifications": [
    #             {
    #                 "name": "サイズ",
    #                 "value": "A4"
    #             },
    #             {
    #                 "name": "色",
    #                 "value": "クリア"
    #             },
    #             {
    #                 "name": "寸法(mm)",
    #                 "value": "317×253×27"
    #             },
    #             {
    #                 "name": "内容量",
    #                 "value": "1個"
    #             }
    #         ],
    #         "categories": "オフィスサプライ > 事務用品 > ファイリング > 収納ボックス/ケース > 書類ケース",
    #         "images": "https://jp.images-monotaro.com/Monotaro3/pi/full/mono23197143-160331-02.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono23197143-210302-02.jpg",
    #         "videos": None,
    #         "price": 1.17,
    #         "available_qty": None,
    #         "options": [{
    #             "id": None,
    #             "name": "品番"
    #         }],
    #         "variants": [{
    #             "variant_id": "23197143",
    #             "barcode": None,
    #             "sku": "23197143",
    #             "option_values": [{
    #                 "option_id": None,
    #                 "option_value_id": None,
    #                 "option_name": "品番",
    #                 "option_value": "3579"
    #             }],
    #             "images": None,
    #             "price": 1.17,
    #             "available_qty": None
    #         }],
    #         "reviews": 15,
    #         "rating": 3.47,
    #         "shipping_fee": 3.26,
    #         "weight": None,
    #         "length": 12.48,
    #         "width": 9.96,
    #         "height": 1.06
    #     }
    #     for key in target_product:
    #         self.assertEqual(product[key], target_product[key])

    #     print(product["description"])
    #     self.assertIn("<h4>注意</h4>", product["description"])
    #     self.assertIn("<th>材質</th>", product["description"])
    #     StandardProduct(**product)

    # def test_available_product_3(self):
    #     url = "https://www.monotaro.com/g/06199072/"
    #     with open("trendyol_test/pages/JS8801 酸素濃度計 MCP=Joman 検知ガス酸素(O2) - 【通販モノタロウ】.html", "rb") as file:
    #         body = file.read()

    #     response = HtmlResponse(
    #         url=url,
    #         body=body,
    #     )
    #     result = list(self.spider.parse(response, 0, '06199072'))
    #     self.assertEqual(len(result), 1)
    #     product = result[0]

    #     target_product = {
    #         "url": url,
    #         "product_id": "06199072",
    #         "existence": True,
    #         "title": "酸素濃度計",
    #         "sku": "44631495",
    #         "brand": "MCP=Joman",
    #         "specifications": [
    #             {
    #                 "name": "寸法(mm)",
    #                 "value": "95.9×66.9×52"
    #             },
    #             {
    #                 "name": "測定範囲",
    #                 "value": "0～30%VOL"
    #             },
    #             {
    #                 "name": "質量(g)",
    #                 "value": "147.5(バッテリー含む)"
    #             },
    #             {
    #                 "name": "バッテリー",
    #                 "value": "3.7V 750mAh充電式リチウム電池"
    #             },
    #             {
    #                 "name": "解像度",
    #                 "value": "0.001"
    #             },
    #             {
    #                 "name": "警報方式",
    #                 "value": "ブザー音/フラッシュ/振動(高値と低値の設定が可能)"
    #             },
    #             {
    #                 "name": "動作温度(℃)",
    #                 "value": "‐10～50"
    #             },
    #             {
    #                 "name": "検知ガス",
    #                 "value": "酸素(O2)"
    #             },
    #             {
    #                 "name": "保管温度(℃)",
    #                 "value": "0～40"
    #             },
    #             {
    #                 "name": "バッテリー稼動時間",
    #                 "value": "60時間(作業により異なる場合あり)"
    #             },
    #             {
    #                 "name": "バックライト",
    #                 "value": "有り"
    #             },
    #             {
    #                 "name": "充電端子",
    #                 "value": "micro USB充電ポート"
    #             },
    #             {
    #                 "name": "内容量",
    #                 "value": "1個"
    #             }
    #         ],
    #         "categories": "測定・測量用品 > 測定用品 > 環境測定(自然環境/安全環境) > 酸素濃度計",
    #         "images": "https://jp.images-monotaro.com/Monotaro3/pi/full/mono44631495-230815-02.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono44631495-230815-04.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono44631495-230815-06.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono44631495-240318-04.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono44631495-240318-06.jpg",
    #         "videos": None,
    #         "price": 176.07,
    #         "available_qty": None,
    #         "options": [{
    #             "id": None,
    #             "name": "品番"
    #         }],
    #         "variants": [{
    #             "variant_id": "44631495",
    #             "barcode": None,
    #             "sku": "44631495",
    #             "option_values": [{
    #                 "option_id": None,
    #                 "option_value_id": None,
    #                 "option_name": "品番",
    #                 "option_value": "JS8801"
    #             }],
    #             "images": None,
    #             "price": 176.07,
    #             "available_qty": None
    #         }],
    #         "reviews": None,
    #         "rating": None,
    #         "shipping_fee": 0.00,
    #         "weight": 0.33,
    #         "length": 3.78,
    #         "width": 2.63,
    #         "height": 2.05
    #     }
    #     for key in target_product:
    #         self.assertEqual(product[key], target_product[key])

    #     print(product["description"])
    #     self.assertNotIn("<h4>注意</h4>", product["description"])
    #     self.assertIn("<th>機能</th>", product["description"])
    #     StandardProduct(**product)

    # def test_available_product_4(self):
    #     url = "https://www.monotaro.com/g/06201561/"
    #     with open("trendyol_test/pages/アサヒ おいしい水 天然水 六甲 PET2L 1ケース(2L×6本) アサヒ飲料 【通販モノタロウ】.html", "rb") as file:
    #         body = file.read()

    #     response = HtmlResponse(
    #         url=url,
    #         body=body,
    #     )
    #     result = list(self.spider.parse(response, 0, '06201561'))
    #     self.assertEqual(len(result), 1)
    #     product = result[0]

    #     target_product = {
    #         "url": url,
    #         "product_id": "06201561",
    #         "existence": True,
    #         "title": "アサヒ おいしい水 天然水 六甲 PET2L",
    #         "sku": "44705756",
    #         "brand": "アサヒ飲料",
    #         "specifications": [
    #             {
    #                 "name": "寸法(mm)",
    #                 "value": "104×89.4×311"
    #             },
    #             {
    #                 "name": "質量(g)",
    #                 "value": "2029"
    #             },
    #             {
    #                 "name": "賞味期限",
    #                 "value": "720日"
    #             },
    #             {
    #                 "name": "原材料",
    #                 "value": "水(深井戸水)"
    #             },
    #             {
    #                 "name": "アレルギー",
    #                 "value": "なし"
    #             },
    #             {
    #                 "name": "内容量",
    #                 "value": "1ケース(2L×6本)"
    #             }
    #         ],
    #         "categories": "オフィスサプライ > 食品・飲料 > 水/ミネラルウォーター > ミネラルウォーター",
    #         "images": "https://jp.images-monotaro.com/Monotaro3/pi/full/mono44705756-230822-02.jpg",
    #         "videos": None,
    #         "price": 6.19,
    #         "available_qty": None,
    #         "options": None,
    #         "variants": None,
    #         "reviews": 4,
    #         "rating": 4.50,
    #         "shipping_fee": 3.26,
    #         "weight": 4.47,
    #         "length": 4.09,
    #         "width": 3.52,
    #         "height": 12.24
    #     }
    #     for key in target_product:
    #         self.assertEqual(product[key], target_product[key])

    #     print(product["description"])
    #     self.assertNotIn("<h4>注意</h4>", product["description"])
    #     self.assertIn("<th>栄養成分</th>", product["description"])
    #     StandardProduct(**product)

    # def test_available_product_5(self):
    #     url = "https://www.monotaro.com/g/02362145/"
    #     with open("trendyol_test/pages/クリアホルダー 厚さ0.2mm モノタロウ クリヤーホルダー 【通販モノタロウ】.html", "rb") as file:
    #         body = file.read()

    #     response = HtmlResponse(
    #         url=url,
    #         body=body,
    #     )
    #     result = list(self.spider.parse(response, 0, '02362145'))
    #     self.assertEqual(len(result), 1)
    #     product = result[0]

    #     target_product = {
    #         "url": url,
    #         "product_id": "02362145",
    #         "existence": True,
    #         "title": "クリアホルダー 厚さ0.2mm",
    #         "sku": "48713035",
    #         "brand": "モノタロウ",
    #         "specifications": [
    #             {
    #                 "name": "サイズ",
    #                 "value": "A4"
    #             },
    #             {
    #                 "name": "色",
    #                 "value": "クリア"
    #             },
    #             {
    #                 "name": "厚さ(mm)",
    #                 "value": "0.2"
    #             },
    #             {
    #                 "name": "寸法(mm)",
    #                 "value": "308×219"
    #             }
    #         ],
    #         "categories": "オフィスサプライ > 事務用品 > ファイリング > クリヤーホルダー",
    #         "images": "https://jp.images-monotaro.com/Monotaro3/pi/full/mono48713044-221004-01.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono48713035-170706-04.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono48713035-221004-02.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono54841650-240612-02.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono54841650-240612-06.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono54841650-240614-02.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono54841659-240612-02.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono54841659-240614-02.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono73387082-230905-02.jpg",
    #         "videos": "https://www.youtube.com/embed/U9V_QlSnrik",
    #         "price": 0.84,
    #         "available_qty": None,
    #         "options": [
    #             {
    #                 "id": None,
    #                 "name": "品番"
    #             },
    #             {
    #                 "id": None,
    #                 "name": "内容量"
    #             }
    #         ],
    #         "variants": [
    #             {
    #                 "variant_id": "48713035",
    #                 "barcode": None,
    #                 "sku": "48713035",
    #                 "option_values": [
    #                     {
    #                         "option_id": None,
    #                         "option_value_id": None,
    #                         "option_name": "品番",
    #                         "option_value": "MCH-02A410"
    #                     },
    #                     {
    #                         "option_id": None,
    #                         "option_value_id": None,
    #                         "option_name": "内容量",
    #                         "option_value": "1パック(10枚)"
    #                     }
    #                 ],
    #                 "images": "https://jp.images-monotaro.com/Monotaro3/pi/full/mono48713035-221004-02.jpg",
    #                 "price": 0.84,
    #                 "available_qty": None
    #             },
    #             {
    #                 "variant_id": "54841650",
    #                 "barcode": None,
    #                 "sku": "54841650",
    #                 "option_values": [
    #                     {
    #                         "option_id": None,
    #                         "option_value_id": None,
    #                         "option_name": "品番",
    #                         "option_value": "MCH-02A4100"
    #                     },
    #                     {
    #                         "option_id": None,
    #                         "option_value_id": None,
    #                         "option_name": "内容量",
    #                         "option_value": "1パック(100枚)"
    #                     }
    #                 ],
    #                 "images": "https://jp.images-monotaro.com/Monotaro3/pi/full/mono54841650-240614-02.jpg",
    #                 "price": 7.77,
    #                 "available_qty": 0
    #             },
    #             {
    #                 "variant_id": "54841659",
    #                 "barcode": None,
    #                 "sku": "54841659",
    #                 "option_values": [
    #                     {
    #                         "option_id": None,
    #                         "option_value_id": None,
    #                         "option_name": "品番",
    #                         "option_value": "MCH-02A4600"
    #                     },
    #                     {
    #                         "option_id": None,
    #                         "option_value_id": None,
    #                         "option_name": "内容量",
    #                         "option_value": "1箱(600枚)"
    #                     }
    #                 ],
    #                 "images": "https://jp.images-monotaro.com/Monotaro3/pi/full/mono54841659-240614-02.jpg",
    #                 "price": 43.66,
    #                 "available_qty": 0
    #             }
    #         ],
    #         "reviews": 438,
    #         "rating": 4.69,
    #         "shipping_fee": 3.26,
    #         "weight": None,
    #         "length": 12.13,
    #         "width": 8.62,
    #         "height": None
    #     }
    #     for key in target_product:
    #         self.assertEqual(product[key], target_product[key])

    #     print(product["description"])
    #     self.assertIn("<h4>注意</h4>", product["description"])
    #     self.assertIn("<th>用途</th>", product["description"])
    #     self.assertIn("<th>材質</th>", product["description"])
    #     StandardProduct(**product)

    # def test_available_product_6(self):
    #     url = "https://www.monotaro.com/g/00264157/"
    #     with open("trendyol_test/pages/マグネットシート マットタイプ モノタロウ 【通販モノタロウ】.html", "rb") as file:
    #         body = file.read()

    #     response = HtmlResponse(
    #         url=url,
    #         body=body,
    #     )
    #     result = list(self.spider.parse(response, 0, '00264157'))
    #     self.assertEqual(len(result), 1)
    #     product = result[0]

    #     target_product = {
    #         "url": url,
    #         "product_id": "00264157",
    #         "existence": True,
    #         "title": "マグネットシート マットタイプ",
    #         "sku": "34921634",
    #         "brand": "モノタロウ",
    #         "specifications": [
    #             {
    #                 "name": "厚さ(mm)",
    #                 "value": "0.8"
    #             },
    #             {
    #                 "name": "RoHS指令(10物質対応)",
    #                 "value": "対応"
    #             },
    #             {
    #                 "name": "内容量",
    #                 "value": "1枚"
    #             }
    #         ],
    #         "categories": "オフィスサプライ > 事務用品 > 掲示用品 > 掲示用小物 > マグネット用品 > マグネットシート",
    #         "images": "https://jp.images-monotaro.com/Monotaro3/pi/full/mono60854893-200925-04.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono34921634-130625-02.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono34921634-130625-04.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono34921634-200925-02.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono34921634-240809-02.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono34921643-130625-02.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono34921643-130625-04.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono34921643-200925-02.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono60854805-130625-02.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono60854805-200925-02.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono60854814-130625-02.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono60854814-200925-02.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono60854823-130625-02.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono60854823-200925-02.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono60854832-130625-02.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono60854832-130711-02.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono60854832-200925-02.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono60854841-130625-02.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono60854841-200925-02.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono60854857-130625-02.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono60854857-130711-02.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono60854857-200925-02.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono60854866-130625-02.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono60854866-200925-02.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono60854875-130625-02.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono60854875-200925-02.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono60854884-130625-02.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono60854884-200925-02.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono60854893-130625-02.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono60854893-200925-02.jpg",
    #         "videos": "https://www.youtube.com/embed/IlU3fj1NDLs",
    #         "price": 1.10,
    #         "available_qty": None,
    #         "options": [
    #             {
    #                 "id": None,
    #                 "name": "品番"
    #             },
    #             {
    #                 "id": None,
    #                 "name": "寸法(mm)"
    #             },
    #             {
    #                 "id": None,
    #                 "name": "色"
    #             }
    #         ],
    #         "variants": [
    #             {
    #                 "variant_id": "34921634",
    #                 "barcode": None,
    #                 "sku": "34921634",
    #                 "option_values": [
    #                     {
    #                         "option_id": None,
    #                         "option_value_id": None,
    #                         "option_name": "品番",
    #                         "option_value": "MS-3010W"
    #                     },
    #                     {
    #                         "option_id": None,
    #                         "option_value_id": None,
    #                         "option_name": "寸法(mm)",
    #                         "option_value": "100×300"
    #                     },
    #                     {
    #                         "option_id": None,
    #                         "option_value_id": None,
    #                         "option_name": "色",
    #                         "option_value": "白"
    #                     }
    #                 ],
    #                 "images": None,
    #                 "price": 1.10,
    #                 "available_qty": None
    #             },
    #             {
    #                 "variant_id": "34921643",
    #                 "barcode": None,
    #                 "sku": "34921643",
    #                 "option_values": [
    #                     {
    #                         "option_id": None,
    #                         "option_value_id": None,
    #                         "option_name": "品番",
    #                         "option_value": "MS-3020W"
    #                     },
    #                     {
    #                         "option_id": None,
    #                         "option_value_id": None,
    #                         "option_name": "寸法(mm)",
    #                         "option_value": "200×300"
    #                     },
    #                     {
    #                         "option_id": None,
    #                         "option_value_id": None,
    #                         "option_name": "色",
    #                         "option_value": "白"
    #                     }
    #                 ],
    #                 "images": None,
    #                 "price": 2.15,
    #                 "available_qty": None
    #             },
    #             {
    #                 "variant_id": "60854805",
    #                 "barcode": None,
    #                 "sku": "60854805",
    #                 "option_values": [
    #                     {
    #                         "option_id": None,
    #                         "option_value_id": None,
    #                         "option_name": "品番",
    #                         "option_value": "MS-3010B"
    #                     },
    #                     {
    #                         "option_id": None,
    #                         "option_value_id": None,
    #                         "option_name": "寸法(mm)",
    #                         "option_value": "100×300"
    #                     },
    #                     {
    #                         "option_id": None,
    #                         "option_value_id": None,
    #                         "option_name": "色",
    #                         "option_value": "青"
    #                     }
    #                 ],
    #                 "images": None,
    #                 "price": 1.10,
    #                 "available_qty": None
    #             },
    #             {
    #                 "variant_id": "60854814",
    #                 "barcode": None,
    #                 "sku": "60854814",
    #                 "option_values": [
    #                     {
    #                         "option_id": None,
    #                         "option_value_id": None,
    #                         "option_name": "品番",
    #                         "option_value": "MS-3010G"
    #                     },
    #                     {
    #                         "option_id": None,
    #                         "option_value_id": None,
    #                         "option_name": "寸法(mm)",
    #                         "option_value": "100×300"
    #                     },
    #                     {
    #                         "option_id": None,
    #                         "option_value_id": None,
    #                         "option_name": "色",
    #                         "option_value": "緑"
    #                     }
    #                 ],
    #                 "images": None,
    #                 "price": 1.10,
    #                 "available_qty": None
    #             },
    #             {
    #                 "variant_id": "60854823",
    #                 "barcode": None,
    #                 "sku": "60854823",
    #                 "option_values": [
    #                     {
    #                         "option_id": None,
    #                         "option_value_id": None,
    #                         "option_name": "品番",
    #                         "option_value": "MS-3010R"
    #                     },
    #                     {
    #                         "option_id": None,
    #                         "option_value_id": None,
    #                         "option_name": "寸法(mm)",
    #                         "option_value": "100×300"
    #                     },
    #                     {
    #                         "option_id": None,
    #                         "option_value_id": None,
    #                         "option_name": "色",
    #                         "option_value": "赤"
    #                     }
    #                 ],
    #                 "images": None,
    #                 "price": 1.10,
    #                 "available_qty": None
    #             },
    #             {
    #                 "variant_id": "60854832",
    #                 "barcode": None,
    #                 "sku": "60854832",
    #                 "option_values": [
    #                     {
    #                         "option_id": None,
    #                         "option_value_id": None,
    #                         "option_name": "品番",
    #                         "option_value": "MS-3010Y"
    #                     },
    #                     {
    #                         "option_id": None,
    #                         "option_value_id": None,
    #                         "option_name": "寸法(mm)",
    #                         "option_value": "100×300"
    #                     },
    #                     {
    #                         "option_id": None,
    #                         "option_value_id": None,
    #                         "option_name": "色",
    #                         "option_value": "黄"
    #                     }
    #                 ],
    #                 "images": None,
    #                 "price": 1.10,
    #                 "available_qty": None
    #             },
    #             {
    #                 "variant_id": "60854841",
    #                 "barcode": None,
    #                 "sku": "60854841",
    #                 "option_values": [
    #                     {
    #                         "option_id": None,
    #                         "option_value_id": None,
    #                         "option_name": "品番",
    #                         "option_value": "MS-3010O"
    #                     },
    #                     {
    #                         "option_id": None,
    #                         "option_value_id": None,
    #                         "option_name": "寸法(mm)",
    #                         "option_value": "100×300"
    #                     },
    #                     {
    #                         "option_id": None,
    #                         "option_value_id": None,
    #                         "option_name": "色",
    #                         "option_value": "オレンジ"
    #                     }
    #                 ],
    #                 "images": None,
    #                 "price": 1.10,
    #                 "available_qty": None
    #             },
    #             {
    #                 "variant_id": "60854857",
    #                 "barcode": None,
    #                 "sku": "60854857",
    #                 "option_values": [
    #                     {
    #                         "option_id": None,
    #                         "option_value_id": None,
    #                         "option_name": "品番",
    #                         "option_value": "MS-3020B"
    #                     },
    #                     {
    #                         "option_id": None,
    #                         "option_value_id": None,
    #                         "option_name": "寸法(mm)",
    #                         "option_value": "200×300"
    #                     },
    #                     {
    #                         "option_id": None,
    #                         "option_value_id": None,
    #                         "option_name": "色",
    #                         "option_value": "青"
    #                     }
    #                 ],
    #                 "images": None,
    #                 "price": 2.15,
    #                 "available_qty": None
    #             },
    #             {
    #                 "variant_id": "60854866",
    #                 "barcode": None,
    #                 "sku": "60854866",
    #                 "option_values": [
    #                     {
    #                         "option_id": None,
    #                         "option_value_id": None,
    #                         "option_name": "品番",
    #                         "option_value": "MS-3020G"
    #                     },
    #                     {
    #                         "option_id": None,
    #                         "option_value_id": None,
    #                         "option_name": "寸法(mm)",
    #                         "option_value": "200×300"
    #                     },
    #                     {
    #                         "option_id": None,
    #                         "option_value_id": None,
    #                         "option_name": "色",
    #                         "option_value": "緑"
    #                     }
    #                 ],
    #                 "images": None,
    #                 "price": 2.15,
    #                 "available_qty": None
    #             },
    #             {
    #                 "variant_id": "60854875",
    #                 "barcode": None,
    #                 "sku": "60854875",
    #                 "option_values": [
    #                     {
    #                         "option_id": None,
    #                         "option_value_id": None,
    #                         "option_name": "品番",
    #                         "option_value": "MS-3020R"
    #                     },
    #                     {
    #                         "option_id": None,
    #                         "option_value_id": None,
    #                         "option_name": "寸法(mm)",
    #                         "option_value": "200×300"
    #                     },
    #                     {
    #                         "option_id": None,
    #                         "option_value_id": None,
    #                         "option_name": "色",
    #                         "option_value": "赤"
    #                     }
    #                 ],
    #                 "images": None,
    #                 "price": 2.15,
    #                 "available_qty": None
    #             },
    #             {
    #                 "variant_id": "60854884",
    #                 "barcode": None,
    #                 "sku": "60854884",
    #                 "option_values": [
    #                     {
    #                         "option_id": None,
    #                         "option_value_id": None,
    #                         "option_name": "品番",
    #                         "option_value": "MS-3020Y"
    #                     },
    #                     {
    #                         "option_id": None,
    #                         "option_value_id": None,
    #                         "option_name": "寸法(mm)",
    #                         "option_value": "200×300"
    #                     },
    #                     {
    #                         "option_id": None,
    #                         "option_value_id": None,
    #                         "option_name": "色",
    #                         "option_value": "黄"
    #                     }
    #                 ],
    #                 "images": None,
    #                 "price": 2.15,
    #                 "available_qty": None
    #             },
    #             {
    #                 "variant_id": "60854893",
    #                 "barcode": None,
    #                 "sku": "60854893",
    #                 "option_values": [
    #                     {
    #                         "option_id": None,
    #                         "option_value_id": None,
    #                         "option_name": "品番",
    #                         "option_value": "MS-3020O"
    #                     },
    #                     {
    #                         "option_id": None,
    #                         "option_value_id": None,
    #                         "option_name": "寸法(mm)",
    #                         "option_value": "200×300"
    #                     },
    #                     {
    #                         "option_id": None,
    #                         "option_value_id": None,
    #                         "option_name": "色",
    #                         "option_value": "オレンジ"
    #                     }
    #                 ],
    #                 "images": None,
    #                 "price": 2.15,
    #                 "available_qty": None
    #             }
    #         ],
    #         "reviews": 79,
    #         "rating": 4.32,
    #         "shipping_fee": 3.26,
    #         "weight": None,
    #         "length": None,
    #         "width": None,
    #         "height": None
    #     }
    #     for key in target_product:
    #         self.assertEqual(product[key], target_product[key])

    #     print(product["description"])
    #     self.assertIn("<h4>注意</h4>", product["description"])
    #     self.assertIn("<th>材質(表面/裏面)</th>", product["description"])
    #     StandardProduct(**product)

    # def test_unavailable_product(self):
    #     url = "https://www.monotaro.com/g/06431439/"
    #     with open("trendyol_test/pages/AP-708209 お医者さんの(R)首サポーター Fit 1個 アルファックス 【通販モノタロウ】.html", "rb") as file:
    #         body = file.read()

    #     response = HtmlResponse(
    #         url=url,
    #         body=body,
    #     )
    #     result = list(self.spider.parse(response, 0, '06431439'))
    #     self.assertEqual(len(result), 1)
    #     product = result[0]

    #     target_product = {
    #         "url": url,
    #         "product_id": "06431439",
    #         "existence": False,
    #         "title": "お医者さんの(R)首サポーター Fit",
    #         "sku": "61690687",
    #         "brand": "アルファックス",
    #         "specifications": [
    #             {
    #                 "name": "質量(g)",
    #                 "value": "100"
    #             },
    #             {
    #                 "name": "寸法(cm)",
    #                 "value": "縦8・横57.5・厚み1.7"
    #             },
    #             {
    #                 "name": "首廻り(cm)",
    #                 "value": "30～46"
    #             },
    #             {
    #                 "name": "内容量",
    #                 "value": "1個"
    #             }
    #         ],
    #         "categories": "医療・介護用品 > ヘルスケア > サポーター・テーピング > サポーター > 首用 サポーター",
    #         "images": "https://jp.images-monotaro.com/Monotaro3/pi/full/mono61690687-240311-02.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono61690687-240311-04.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono61690687-240311-06.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono61690687-240311-08.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono61690687-240311-10.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono61690687-240311-12.jpg;https://jp.images-monotaro.com/Monotaro3/pi/full/mono61690687-240311-14.jpg",
    #         "videos": None,
    #         "price": 24.79,
    #         "available_qty": 0,
    #         "options": [{
    #             "id": None,
    #             "name": "品番"
    #         }],
    #         "variants": [{
    #             "variant_id": "61690687",
    #             "barcode": None,
    #             "sku": "61690687",
    #             "option_values": [{
    #                 "option_id": None,
    #                 "option_value_id": None,
    #                 "option_name": "品番",
    #                 "option_value": "AP-708209"
    #             }],
    #             "images": None,
    #             "price": 24.79,
    #             "available_qty": 0
    #         }],
    #         "reviews": None,
    #         "rating": None,
    #         "shipping_fee": 0.00,
    #         "weight": 0.22,
    #         "length": None,
    #         "width": None,
    #         "height": None,
    #     }
    #     for key in target_product:
    #         self.assertEqual(product[key], target_product[key])

    #     print(product["description"])
    #     self.assertNotIn("<h4>注意</h4>", product["description"])
    #     self.assertIn("<th>用途</th>", product["description"])
    #     self.assertIn("<th>材質</th>", product["description"])
    #     StandardProduct(**product)


if __name__ == '__main__':
    unittest.main()