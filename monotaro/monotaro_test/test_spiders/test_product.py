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
        result = list(self.spider.parse(response))
        self.assertEqual(len(result), 1)
        product = result[0]

        target_product = {
            "url": url,
            "product_id": "01429775",
            "existence": True,
            "title": "アロマストーン",
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
                    "name": "材質",
                    "value": "PP"
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
            "weight": 0.37,
            "length": 12.48,
            "width": 9.96,
            "height": 1.06
        }
        for key in target_product:
            self.assertEqual(product[key], target_product[key])
        
        self.assertIn("<h4>注意</h4>", product["description"])
        print(product["description"])

    def test_available_product_2(self):
        url = "https://www.muji.com/jp/ja/store/cmdty/detail/4550344594056"
        with open("monotaro_test/pages/インテリアフレグランスオイル _ 無印良品.html", "rb") as file:
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
            "product_id": "44594056",
            "existence": True,
            "title": "インテリアフレグランスオイル",
            "sku": "4550344594056",
            "upc": "4550344594056",
            "brand": "無印良品",
            "specifications": [
                {
                    "name": "原産国・地域",
                    "value": "日本"
                },
                {
                    "name": "仕様・混率",
                    "value": "インテリアフレグランスオイル"
                },
                {
                    "name": "容量",
                    "value": "60mL"
                },
                {
                    "name": "部材ごとの素材",
                    "value": "本体：ガラス"
                },
                {
                    "name": "重量（梱包材含む）",
                    "value": "約170g"
                }
            ],
            "categories": "生活雑貨 > アロマ・ルームフレグランス > インテリアフレグランス",
            "images": "https://www.muji.com/public/media/img/item/4550344594056_org.jpg;https://www.muji.com/public/media/img/item/4550344594056_01_org.jpg;https://www.muji.com/public/media/img/item/4550344594056_02_org.jpg;https://www.muji.com/public/media/img/item/4550344594056_03_org.jpg;https://www.muji.com/public/media/img/item/4550344594056_04_org.jpg",
            "price": 7.81,
            "available_qty": None,
            "reviews": 234,
            "rating": 4.60,
            "shipping_fee": 3.28,
            "weight": 0.37
        }
        for key in target_product:
            self.assertEqual(product[key], target_product[key])

    def test_available_product_3(self):
        url = "https://www.muji.com/jp/ja/store/cmdty/detail/4550344554586"
        with open("monotaro_test/pages/超音波うるおいアロマディフューザー _ 無印良品.html", "rb") as file:
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
            "product_id": "44554586",
            "existence": True,
            "title": "超音波うるおいアロマディフューザー",
            "sku": "4550344554586",
            "upc": "4550344554586",
            "brand": "無印良品",
            "specifications": [
                {
                    "name": "原産国・地域",
                    "value": "中国"
                },
                {
                    "name": "外寸",
                    "value": "直径16.8cm×高さ12.1cm　　重さ約490g（本体のみ）"
                },
                {
                    "name": "容量",
                    "value": "タンク容量：約350ml"
                },
                {
                    "name": "型名",
                    "value": "MJ-UAD1"
                },
                {
                    "name": "部材ごとの素材",
                    "value": "本体、主要部品共にＰＰ"
                },
                {
                    "name": "消費電力",
                    "value": "約15W"
                },
                {
                    "name": "連続使用時の稼働時間",
                    "value": "約3時間（専用USB_ACアダプター使用、満水時）"
                },
                {
                    "name": "主な機能・性能",
                    "value": "LED照明：2段階　　タイマー機能：60分、120分"
                },
                {
                    "name": "付属物情報",
                    "value": "AC_アダプター、計量カップ、抗菌カートリッジ"
                },
                {
                    "name": "コード長",
                    "value": "約1.8m"
                },
                {
                    "name": "重量（梱包材含む）",
                    "value": "約500g"
                }
            ],
            "categories": "家具・収納・家電 > 家電・照明器具・時計 > 生活家電・AV家電",
            "images": "https://www.muji.com/public/media/img/item/4550344554586_org.jpg;https://www.muji.com/public/media/img/item/4550344554586_01_org.jpg;https://www.muji.com/public/media/img/item/4550344554586_02_org.jpg;https://www.muji.com/public/media/img/item/4550344554586_03_org.jpg;https://www.muji.com/public/media/img/item/4550344554586_04_org.jpg;https://www.muji.com/public/media/img/item/4550344554586_05_org.jpg;https://www.muji.com/public/media/img/item/4550344554586_06_org.jpg;https://www.muji.com/public/media/img/item/4550344554586_07_org.jpg;https://www.muji.com/public/media/img/item/4550344554586_08_org.jpg;https://www.muji.com/public/media/img/item/4550344554586_09_org.jpg;https://www.muji.com/public/media/img/item/4550344554586_10_org.jpg;https://www.muji.com/public/media/img/item/4550344554586_11_org.jpg;https://www.muji.com/public/media/img/item/4550344554586_12_org.jpg",
            "price": 45.89,
            "available_qty": None,
            "reviews": 65,
            "rating": 4.50,
            "shipping_fee": 0.00,
            "weight": 1.10
        }
        for key in target_product:
            self.assertEqual(product[key], target_product[key])

    def test_unavailable_product(self):
        url = "https://www.muji.com/jp/ja/store/cmdty/detail/4550344295236"
        with open("monotaro_test/pages/フレグランスミスト　くつろぎブレンド _ 無印良品.html", "rb") as file:
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
            "product_id": "44295236",
            "existence": False,
            "title": "フレグランスミスト　くつろぎブレンド",
            "sku": "4550344295236",
            "upc": "4550344295236",
            "brand": "無印良品",
            "specifications": [
                {
                    "name": "原産国・地域",
                    "value": "日本"
                },
                {
                    "name": "仕様・混率",
                    "value": "フレグランスミスト　くつろぎブレンド"
                },
                {
                    "name": "外寸",
                    "value": "W3.2cmxD3.2cmxH12.9cm(ケース入）"
                },
                {
                    "name": "容量",
                    "value": "28mL"
                },
                {
                    "name": "部材ごとの素材",
                    "value": "箱：紙　ポンプ：PP、PE　キャップ：PP"
                },
                {
                    "name": "アルコール使用",
                    "value": "使用"
                },
                {
                    "name": "スプレーｏｒポンプヘッド",
                    "value": "スプレーヘッド"
                },
                {
                    "name": "光毒性の有無",
                    "value": "無"
                },
                {
                    "name": "重量（梱包材含む）",
                    "value": "約90g"
                }
            ],
            "categories": "生活雑貨 > アロマ・ルームフレグランス > フレグランス",
            "images": "https://www.muji.com/public/media/img/item/4550344295236_org.jpg;https://www.muji.com/public/media/img/item/4550344295236_01_org.jpg;https://www.muji.com/public/media/img/item/4550344295236_02_org.jpg;https://www.muji.com/public/media/img/item/4550344295236_03_org.jpg",
            "price": 11.09,
            "available_qty": 0,
            "reviews": 83,
            "rating": 4.70,
            "shipping_fee": 3.28,
            "weight": 0.20
        }
        for key in target_product:
            self.assertEqual(product[key], target_product[key])


if __name__ == '__main__':
    unittest.main()
