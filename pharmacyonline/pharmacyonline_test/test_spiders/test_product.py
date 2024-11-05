import unittest

from scrapy.utils.test import get_crawler
from scrapy.http import HtmlResponse

from pharmacyonline.spiders.po_product import POProductSpider


# python -m pharmacyonline_test.test_spiders.test_product
class TestProduct(unittest.TestCase):
    def setUp(self):
        self.crawler = get_crawler(POProductSpider)
        self.spider = self.crawler._create_spider()

    def test_available_product_1(self):
        url = "https://www.pharmacyonline.com.au/quality-health-vitamin-d-calcium-tab-x-130"
        with open("pharmacyonline_test/pages/Quality Health Vitamin D & Calcium Tab X 130 - Buy Online in Australia - Pharmacy Online.html", "rb") as file:
            body = file.read()

        response = HtmlResponse(
            url=url,
            body=body,
        )
        result = list(self.spider.parse(response, 280.0))
        self.assertEqual(len(result), 1)
        product = result[0]

        target_product = {
            "url": url,
            "product_id": "10002747",
            "existence": True,
            "title": "Quality Health Vitamin D & Calcium Tab X 130",
            "sku": "10002747",
            "upc": "9314807059507",
            "brand": "Finishing Touch Flawless",
            "categories": "Vitamins & Supplements > Vitamins > Bone & Joints Health > By Condition > Arthritis & Joints",
            "images": "https://www.pharmacyonline.com.au/media/catalog/product/7/7/770033_vitamin_d_calcium_600mg_130s.jpg",
            "videos": None,
            "price": 6.56,
            "available_qty": None,
            "reviews": 0,
            "rating": 0.00,
            "shipping_fee": 6.56,
            "weight": 0.62
        }
        for key in target_product:
            self.assertEqual(product[key], target_product[key])

        # 检查描述有效性
        self.assertNotIn('</a>', product['description'])
        self.assertNotIn('</script>', product['description'])
        self.assertNotIn('online in Australia from Pharmacy Online', product['description'])
        self.assertIn('<h1>Product Description & Features</h1>', product['description'])
        self.assertIn('<h1>Directions For Use</h1>', product['description'])
        self.assertIn('<h1>Ingredients/Material</h1>', product['description'])
        self.assertIn('<h1>Warnings and Disclaimers</h1>', product['description'])

    def test_available_product_2(self):
        url = "https://www.pharmacyonline.com.au/first-response-instream-pregnancy-test-x-6-1"
        with open("pharmacyonline_test/pages/First Response In-Stream Pregnancy Test x 6+1 - Buy Online in Australia - Pharmacy Online.html", "rb") as file:
            body = file.read()

        response = HtmlResponse(
            url=url,
            body=body,
        )
        result = list(self.spider.parse(response, 106.0))
        self.assertEqual(len(result), 1)
        product = result[0]

        target_product = {
            "url": url,
            "product_id": "10001565",
            "existence": True,
            "title": "First Response In-Stream Pregnancy Test x 6+1",
            "sku": "10001565",
            "upc": "19310320002300",
            "brand": "First Response",
            "categories": "Pregnancy Kits > Personal Care & Beauty > Health & First Aids > Health Aids > Pregnancy Tests > Sexual Health > Pregnancy & Fertility",
            "images": "https://www.pharmacyonline.com.au/media/catalog/product/f/i/first_response_in-stream_pregnancy_test_x_6_1_-1.jpg;https://www.pharmacyonline.com.au/media/catalog/product/f/i/first_response_in-stream_pregnancy_test_x_6_1_-2.jpg;https://www.pharmacyonline.com.au/media/catalog/product/f/i/first_response_in-stream_pregnancy_test_x_6_1_-3.jpg;https://www.pharmacyonline.com.au/media/catalog/product/f/i/first_response_in-stream_pregnancy_test_x_6_1_-4.jpg;https://www.pharmacyonline.com.au/media/catalog/product/f/i/first_response_in-stream_pregnancy_test_x_6_1_-5.jpg",
            "video": None,
            "price": 17.76,
            "available_qty": None,
            "reviews": 0,
            "rating": 0.00,
            "shipping_fee": 6.56,
            "weight": 0.23
        }

        for key in target_product:
            self.assertEqual(product[key], target_product[key])

    def test_available_product_3(self):
        url = "https://www.muji.com/jp/ja/store/cmdty/detail/4550344554586"
        with open("pharmacyonline_test/pages/超音波うるおいアロマディフューザー _ 無印良品.html", "rb") as file:
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
        with open("pharmacyonline_test/pages/フレグランスミスト　くつろぎブレンド _ 無印良品.html", "rb") as file:
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
