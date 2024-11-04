import unittest

from scrapy.utils.test import get_crawler
from scrapy.http import HtmlResponse

from muji.muji.spiders.product import MujiProduct


class TestProduct(unittest.TestCase):
    def setUp(self):
        self.crawler = get_crawler(MujiProduct)
        self.spider = self.crawler._create_spider()

    def test_available_product_1(self):
        url = "https://www.muji.com/jp/ja/store/cmdty/detail/4550002868284"
        with open("muji_test/pages/アロマストーン _ 無印良品.html", "rb") as file:
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
            "product_id": "02868284",
            "existence": True,
            "title": "アロマストーン",
            "sku": "4550002868284",
            "upc": "4550002868284",
            "brand": "無印良品",
            "specifications": [
                {
                    "name": "原産国・地域",
                    "value": "日本"
                },
                {
                    "name": "仕様・混率",
                    "value": "アロマストーン"
                },
                {
                    "name": "外寸",
                    "value": "ストーン約直径65ｍｍ×30mm　トレー約直径63mm×5mm"
                },
                {
                    "name": "リフィル等パーツ",
                    "value": "替皿"
                },
                {
                    "name": "重量（梱包材含む）",
                    "value": "約170g"
                },
            ],
            "categories": "生活雑貨 > アロマ・ルームフレグランス > アロマディフューザー",
            "images": "https://www.muji.com/public/media/img/item/4550002868284_org.jpg;https://www.muji.com/public/media/img/item/4550002868284_01_org.jpg;https://www.muji.com/public/media/img/item/4550002868284_02_org.jpg",
            "price": 6.50,
            "available_qty": None,
            "reviews": 438,
            "rating": 3.80,
            "shipping_fee": 3.28,
            "weight": 0.37
        }

        for key in target_product:
            self.assertEqual(product[key], target_product[key])

    def test_available_product_2(self):
        url = "https://www.muji.com/jp/ja/store/cmdty/detail/4550344594056"
        with open("muji_test/pages/アロマストーン _ 無印良品.html", "rb") as file:
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
                    "name": "外寸",
                    "value": "ストーン約直径65ｍｍ×30mm　トレー約直径63mm×5mm"
                },
                {
                    "name": "リフィル等パーツ",
                    "value": "替皿"
                },
                {
                    "name": "重量（梱包材含む）",
                    "value": "約170g"
                },
            ],
            "categories": "生活雑貨 > アロマ・ルームフレグランス > インテリアフレグランス",
            "images": "https://www.muji.com/public/media/img/item/4550002868284_org.jpg;https://www.muji.com/public/media/img/item/4550002868284_01_org.jpg;https://www.muji.com/public/media/img/item/4550002868284_02_org.jpg",
            "price": 6.50,
            "available_qty": None,
            "reviews": 438,
            "rating": 3.80,
            "shipping_fee": 3.28,
            "weight": 0.37
        }

        for key in target_product:
            self.assertEqual(product[key], target_product[key])

