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
            "has_only_default_variant": True,
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

    def test_available_product_2(self):
        url = "https://www.trendyol.com/copierbond/ve-ge-a4-fotokopi-kagidi-80-g-500-lu-5-paket-2500ad-1-koli-p-6026206"
        with open("trendyol_test/pages/Copier Bond A4 Kağıdı 80 g 5'li Paket 80 g 500 Yaprak 2500 Adet Fiyatı - Trendyol.html", "rb") as file:
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

        url2 = "https://apigw.trendyol.com/discovery-web-productgw-service/api/product-detail/6026206/html-content?channelId=1"
        with open("trendyol_test/pages/6026206.json", "rb") as file2:
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
            "product_id": "6026206",
            "existence": True,
            "title": "Ve-ge A4 Fotokopi Kağıdı 80 G 500'lü 5 Paket 2500ad. 1 Koli.",
            "sku": "6026206",
            "upc": "8690460421297",
            "brand": "Copierbond",
            "specifications": [
                {
                    "name": "Kağıt Boyutu",
                    "value": "A4"
                },
                {
                    "name": "Gramaj",
                    "value": "80 gr"
                },
                {
                    "name": "Kağıt Tipi",
                    "value": "Beyaz Fotokopi Kağıdı"
                },
                {
                    "name": "Okula Dönüş",
                    "value": "Ortaokul"
                }
            ],
            "categories": "Copierbond > Kırtasiye Ofis Malzemeleri > Kırtasiye Kağıt Ürünleri > Fotokopi & Baskı Kağıtları",
            "images": "https://cdn.dsmcdn.com/ty1591/prod/QC/20241023/11/94095151-57f3-3f6e-bf80-8f5d2cc441fb/1_org_zoom.jpg;https://cdn.dsmcdn.com/ty1590/prod/QC/20241023/11/e677a0db-1d21-351b-86e7-a26d38d2332d/1_org_zoom.jpg",
            "videos": None,
            "price": 14.53,
            "available_qty": None,
            "options": None,
            "variants": None,
            "has_only_default_variant": True,
            "reviews": 17531,
            "rating": 4.70,
            "shipping_fee": 0.00,
            "weight": 0.18,
            "length": None,
            "width": None,
            "height": None
        }
        for key in target_product:
            self.assertEqual(product[key], target_product[key])

        print(product["description"])
        StandardProduct(**product)

    def test_available_product_3(self):
        url = "https://www.trendyol.com/bubito/kislik-tatli-kapsonlu-bebek-pelus-welsoft-tulum-p-446949530"
        with open("trendyol_test/pages/Kışlık Tatlı Kapşonlu Bebek Peluş Welsoft Tulum Bubito _ Trendyol.html", "rb") as file:
            body = file.read()
        resp1 = HtmlResponse(
            url=url,
            body=body,
        )
        result = list(self.spider.parse(resp1))
        self.assertEqual(len(result), 1)
        product = result[0]["item"]

        has_more_descr = result[0]["has_more_descr"]
        video_id = result[0]["video_id"]
        self.assertFalse(has_more_descr)
        self.assertIsNone(video_id)

        target_product = {
            "url": url,
            "product_id": "446949530",
            "existence": True,
            "title": "Kışlık Tatlı Kapşonlu Bebek Peluş Welsoft Tulum",
            "sku": "446949530",
            "upc": "BB2021BB000900903",
            "brand": "Bubito",
            "specifications": [
                {
                    "name": "Materyal",
                    "value": "Pamuklu"
                },
                {
                    "name": "Desen",
                    "value": "Düz"
                },
                {
                    "name": "Renk",
                    "value": "Kahverengi"
                },
                {
                    "name": "Yaka Tipi",
                    "value": "Kapüşonlu"
                },
                {
                    "name": "Materyal Bileşeni",
                    "value": "%100 Pamuk"
                },
                {
                    "name": "Kumaş Tipi",
                    "value": "Dokuma"
                },
                {
                    "name": "Boy",
                    "value": "Standart"
                },
                {
                    "name": "Kalıp",
                    "value": "Dar"
                },
                {
                    "name": "Paça Tipi",
                    "value": "Dar Paça"
                },
                {
                    "name": "Kol Boyu",
                    "value": "Uzun"
                },
                {
                    "name": "Kol Tipi",
                    "value": "Standart Kol"
                },
                {
                    "name": "Koleksiyon",
                    "value": "Basic"
                },
                {
                    "name": "Sürdürülebilirlik Detayı",
                    "value": "Hayır"
                },
                {
                    "name": "Paket İçeriği",
                    "value": "Tekli"
                },
                {
                    "name": "Ortam",
                    "value": "Casual/Günlük"
                }
            ],
            "categories": "Çocuk > Çocuk Giyim > Çocuk Bebek Giyim > Çocuk Bebek Takımı",
            "images": "https://cdn.dsmcdn.com/ty809/product/media/images/20230331/21/316483741/640446403/1/1_org_zoom.jpg;https://cdn.dsmcdn.com/ty808/product/media/images/20230331/21/316483741/640446403/2/2_org_zoom.jpg;https://cdn.dsmcdn.com/ty808/product/media/images/20230331/21/316483741/640446403/3/3_org_zoom.jpg;https://cdn.dsmcdn.com/ty809/product/media/images/20230331/21/316483741/640446403/4/4_org_zoom.jpg;https://cdn.dsmcdn.com/ty808/product/media/images/20230331/21/316483741/640446403/5/5_org_zoom.jpg",
            "videos": None,
            "price": 5.33,
            "available_qty": None,
            "options": [{
                "id": "338",
                "name": "Beden"
            }],
            "variants": [
                {
                    "variant_id": "640685543",
                    "barcode": "BB2021BB000900903",
                    "sku": "640685543",
                    "option_values": [{
                        "option_id": "338",
                        "option_value_id": None,
                        "option_name": "Beden",
                        "option_value": "0-3 AY"
                    }],
                    "images": None,
                    "price": 5.82,
                    "available_qty": None 
                },
                {
                    "variant_id": "640446403",
                    "barcode": "BB2021BB000900904",
                    "sku": "640446403",
                    "option_values": [{
                        "option_id": "338",
                        "option_value_id": None,
                        "option_name": "Beden",
                        "option_value": "3-6 AY"
                    }],
                    "images": None,
                    "price": 5.82,
                    "available_qty": None 
                },
                {
                    "variant_id": "640666052",
                    "barcode": "BB2021BB000900905",
                    "sku": "640666052",
                    "option_values": [{
                        "option_id": "338",
                        "option_value_id": None,
                        "option_name": "Beden",
                        "option_value": "6-9 AY"
                    }],
                    "images": None,
                    "price": 5.82,
                    "available_qty": None 
                },
                {
                    "variant_id": "1055598253",
                    "barcode": "BB2022BB202301933",
                    "sku": "1055598253",
                    "option_values": [{
                        "option_id": "338",
                        "option_value_id": None,
                        "option_name": "Beden",
                        "option_value": "9 - 12 Ay"
                    }],
                    "images": None,
                    "price": 5.82,
                    "available_qty": None 
                }
            ],
            "has_only_default_variant": False,
            "reviews": 1458,
            "rating": 4.31,
            "shipping_fee": 1.16,
            "weight": None,
            "length": None,
            "width": None,
            "height": None
        }
        for key in target_product:
            self.assertEqual(product[key], target_product[key])

        print(product["description"])
        self.assertIn("<th>Yıkama Talimatı</th>", product["description"])
        StandardProduct(**product)

    def test_available_product_4(self):
        url = "https://www.trendyol.com/l-oreal-paris/panorama-hacim-veren-maskara-koyu-kahverengi-p-796043319"
        with open("trendyol_test/pages/L'Oreal Paris Panorama Hacim Veren Maskara Koyu Kahverengi Fiyatı, Yorumları - Trendyol.html", "rb") as file:
            body = file.read()
        resp1 = HtmlResponse(
            url=url,
            body=body,
        )
        result = list(self.spider.parse(resp1))
        self.assertEqual(len(result), 1)
        product = result[0]["item"]

        has_more_descr = result[0]["has_more_descr"]
        video_id = result[0]["video_id"]
        self.assertFalse(has_more_descr)
        self.assertIsNone(video_id)

        target_product = {
            "url": url,
            "product_id": "796043319",
            "existence": True,
            "title": "Panorama Hacim Veren Maskara Koyu Kahverengi",
            "sku": "796043319",
            "upc": "30158672",
            "brand": "L'Oreal Paris",
            "specifications": [
                {
                    "name": "Boy",
                    "value": "Orijinal Boy"
                },
                {
                    "name": "Suya/Tere Dayanıklılık",
                    "value": "Yok"
                },
                {
                    "name": "Fırça Tipi",
                    "value": "Plastik"
                },
                {
                    "name": "Etki",
                    "value": "Hacim Verici"
                }
            ],
            "categories": "L'Oreal Paris > Kozmetik > Makyaj > Göz Makyajı > Maskara",
            "images": "https://cdn.dsmcdn.com/ty1535/product/media/images/prod/QC/20240910/11/327a3f0f-e206-3f1c-865a-b026f4db0d8d/1_org_zoom.jpg;https://cdn.dsmcdn.com/ty1534/product/media/images/prod/QC/20240910/11/f0d3b4d3-e13b-39aa-a375-1b09170c3f65/1_org_zoom.jpg;https://cdn.dsmcdn.com/ty1535/product/media/images/prod/QC/20240910/11/b9c94ff8-5a7a-33ea-8e22-c0ec7f0bb962/1_org_zoom.jpg;https://cdn.dsmcdn.com/ty1535/product/media/images/prod/QC/20240910/11/0b4f0b4a-0200-3543-93b3-640c4cc685df/1_org_zoom.jpg;https://cdn.dsmcdn.com/ty1534/product/media/images/prod/QC/20240910/11/28803917-4a40-3aa0-80c9-5857f5163260/1_org_zoom.jpg;https://cdn.dsmcdn.com/ty1535/product/media/images/prod/QC/20240910/11/cb3cc353-1927-3c73-9f9f-350c8a0a7c5f/1_org_zoom.jpg;https://cdn.dsmcdn.com/ty1535/product/media/images/prod/QC/20240910/11/3688cbf7-d349-3f73-8f73-7c2f753ab174/1_org_zoom.jpg;https://cdn.dsmcdn.com/ty1533/product/media/images/prod/QC/20240910/11/47ce4fd9-7225-3723-a7b9-c561dc11853b/1_org_zoom.jpg",
            "videos": None,
            "price": 11.96,
            "available_qty": None,
            "options": None,
            "variants": None,
            "has_only_default_variant": True,
            "reviews": 619,
            "rating": 4.22,
            "shipping_fee": 0.00,
            "weight": None,
            "length": None,
            "width": None,
            "height": None
        }
        for key in target_product:
            self.assertEqual(product[key], target_product[key])

        print(product["description"])
        StandardProduct(**product)

    def test_available_product_5(self):
        url = "https://www.trendyol.com/mert-sert-mobilya/vern-120cm-konsol-tv-sehpasi-tv-unitesi-kahve-kosesi-banyo-dolabi-cok-amacli-dolap-p-773280008"
        with open("trendyol_test/pages/MERT SERT MOBİLYA Vern 120cm Konsol, Tv Sehpası, Tv Ünitesi, Kahve Köşesi, Banyo Dolabı, Çok Amaçlı Dolap Fiyatı, Yorumları - Trendyol.html", "rb") as file:
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
        self.assertFalse(has_more_descr)
        self.assertEqual(video_id, "67c617e7-395d-4873-ba14-f556de685d61")

        url3 = "https://apigw.trendyol.com/discovery-web-websfxmediacenter-santral/video-content-by-id/67c617e7-395d-4873-ba14-f556de685d61?channelId=1"
        with open("trendyol_test/pages/67c617e7-395d-4873-ba14-f556de685d61.json", "rb") as file3:
            body3 = file3.read()
        response = HtmlResponse(
            url=url3,
            body=body3
        )
        result = list(self.spider.parse_video(response, prod1))
        self.assertEqual(len(result), 1)
        product = result[0]

        target_product = {
            "url": url,
            "product_id": "773280008",
            "existence": True,
            "title": "Vern 120cm Konsol, Tv Sehpası, Tv Ünitesi, Kahve Köşesi, Banyo Dolabı, Çok Amaçlı Dolap",
            "sku": "773280008",
            "upc": "MERTSERTKNS29",
            "brand": "MERT SERT MOBİLYA",
            "specifications": [
                {
                    "name": "Materyal",
                    "value": "Suntalam"
                },
                {
                    "name": "Derinlik",
                    "value": "30 cm"
                },
                {
                    "name": "Yükseklik",
                    "value": "75 cm"
                },
                {
                    "name": "Fonksiyon",
                    "value": "Kapaklı + Raflı"
                },
                {
                    "name": "Özellik",
                    "value": "Ayaklı"
                },
                {
                    "name": "Renk",
                    "value": "Beyaz"
                },
                {
                    "name": "Garanti Süresi",
                    "value": "2 Yıl"
                },
                {
                    "name": "Genişlik",
                    "value": "120 cm"
                },
                {
                    "name": "Stil",
                    "value": "Modern"
                },
                {
                    "name": "Tema / Stil",
                    "value": "Modern"
                }
            ],
            "categories": "MERT SERT MOBİLYA > Ev ve Mobilya > Mobilya > Yemek Odası Mobilyası > Konsol",
            "images": "https://cdn.dsmcdn.com/ty1536/product/media/images/prod/QC/20240911/15/6cdedcf6-39ac-3e14-801f-394e122f0822/1_org_zoom.jpg;https://cdn.dsmcdn.com/ty1537/product/media/images/prod/QC/20240911/15/e819c0fc-5caa-35cd-bf51-b3c76a60bb45/1_org_zoom.jpg;https://cdn.dsmcdn.com/ty1538/product/media/images/prod/QC/20240911/15/b702b5de-293b-3bdb-93a9-873c20976fc6/1_org_zoom.jpg;https://cdn.dsmcdn.com/ty1538/product/media/images/prod/QC/20240911/15/0df843ed-7348-36ba-808e-c288c0fac835/1_org_zoom.jpg;https://cdn.dsmcdn.com/ty1538/product/media/images/prod/QC/20240911/15/24a8ae58-bb39-3895-8e2c-fc1cd7a4b409/1_org_zoom.jpg",
            "videos": "https://video-content.dsmcdn.com/prod/720p/2017928/2025904/2045844/67c617e7-395d-4873-ba14-f556de685d61.mp4",
            "price": 49.94,
            "available_qty": None,
            "options": None,
            "variants": None,
            "has_only_default_variant": True,
            "reviews": 332,
            "rating": 4.42,
            "shipping_fee": 0.00,
            "weight": None,
            "length": None,
            "width": 47.24,
            "height": 29.53
        }
        for key in target_product:
            self.assertEqual(product[key], target_product[key])

        print(product["description"])
        StandardProduct(**product)

    def test_available_product_6(self):
        url = "https://www.trendyol.com/the-fine-organics/avustralya-nanesi-aktif-karbon-dis-beyazlatma-tozu-50g-p-762586955"
        with open("trendyol_test/pages/THE FINE ORGANICS Avustralya Nanesi & Aktif Karbon Diş Beyazlatma Tozu, 50g Fiyatı, Yorumları - Trendyol.html", "rb") as file:
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
        self.assertFalse(has_more_descr)
        self.assertEqual(video_id, "c931a628-affd-4591-9fcd-f47c40cf4aa3")

        url3 = "https://apigw.trendyol.com/discovery-web-websfxmediacenter-santral/video-content-by-id/c931a628-affd-4591-9fcd-f47c40cf4aa3?channelId=1"
        with open("trendyol_test/pages/c931a628-affd-4591-9fcd-f47c40cf4aa3.json", "rb") as file3:
            body3 = file3.read()
        response = HtmlResponse(
            url=url3,
            body=body3
        )
        result = list(self.spider.parse_video(response, prod1))
        self.assertEqual(len(result), 1)
        product = result[0]

        target_product = {
            "url": url,
            "product_id": "762586955",
            "existence": True,
            "title": "Avustralya Nanesi & Aktif Karbon Diş Beyazlatma Tozu, 50g",
            "sku": "762586955",
            "upc": "8684255820167",
            "brand": "THE FINE ORGANICS",
            "specifications": [{
                "name": "Form",
                "value": "Beyazlatıcı Toz"
            }],
            "categories": "Kozmetik > Ağız Bakım",
            "images": "https://cdn.dsmcdn.com/ty1457/product/media/images/prod/QC/20240802/17/03ea47c1-fc57-31bc-906c-71266273a7b6/1_org_zoom.jpg;https://cdn.dsmcdn.com/ty1457/product/media/images/prod/QC/20240802/17/be40a592-f810-3c28-aa65-cae17972c32d/1_org_zoom.jpg;https://cdn.dsmcdn.com/ty1455/product/media/images/prod/QC/20240802/17/0435e079-1880-328a-8141-38993de77d03/1_org_zoom.jpg;https://cdn.dsmcdn.com/ty1456/product/media/images/prod/QC/20240802/17/f830a409-d950-31f7-affb-3260b3dfb8f4/1_org_zoom.jpg;https://cdn.dsmcdn.com/ty1455/product/media/images/prod/QC/20240802/17/d4ae8dcb-c048-37d1-b1fd-70e5aa7e6a30/1_org_zoom.jpg;https://cdn.dsmcdn.com/ty1455/product/media/images/prod/QC/20240802/17/fd91346b-e26f-34f5-8f86-3af62eb2636e/1_org_zoom.jpg",
            "videos": "https://video-content.dsmcdn.com/prod/720p/2017928/2020919/2027898/c931a628-affd-4591-9fcd-f47c40cf4aa3.mp4",
            "price": 4.22,
            "available_qty": None,
            "options": None,
            "variants": None,
            "has_only_default_variant": True,
            "reviews": 580,
            "rating": 4.21,
            "shipping_fee": 1.16,
            "weight": None,
            "length": None,
            "width": None,
            "height": None
        }
        for key in target_product:
            self.assertEqual(product[key], target_product[key])

        print(product["description"])
        StandardProduct(**product)

    def test_available_product_7(self):
        url = "https://www.trendyol.com/talay/ortodontik-parantez-egri-dis-duzeltme-seti-d1-yumusak-d2-orta-d3-sert-p-260796603"
        with open("trendyol_test/pages/TALAY Ortodontik Parantez Eğri Diş Düzeltme Seti D1 Yumuşak D2 Orta D3 Sert Fiyatı, Yorumları - Trendyol.html", "rb") as file:
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

        url2 = "https://apigw.trendyol.com/discovery-web-productgw-service/api/product-detail/260796603/html-content?channelId=1"
        with open("trendyol_test/pages/260796603.json", "rb") as file2:
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
            "product_id": "260796603",
            "existence": True,
            "title": "Ortodontik Parantez Eğri Diş Düzeltme Seti D1 Yumuşak D2 Orta D3 Sert",
            "sku": "260796603",
            "upc": "7732555736114",
            "brand": "TALAY",
            "specifications": None,
            "categories": "Kozmetik > Ağız Bakım",
            "images": "https://cdn.dsmcdn.com/ty359/product/media/images/20220312/21/68836360/413993781/1/1_org_zoom.jpg;https://cdn.dsmcdn.com/ty359/product/media/images/20220312/21/68836360/413993781/2/2_org_zoom.jpg;https://cdn.dsmcdn.com/ty358/product/media/images/20220312/21/68836360/413993781/3/3_org_zoom.jpg;https://cdn.dsmcdn.com/ty358/product/media/images/20220312/21/68836360/413993781/4/4_org_zoom.jpg;https://cdn.dsmcdn.com/ty357/product/media/images/20220312/21/68836360/413993781/5/5_org_zoom.jpg;https://cdn.dsmcdn.com/ty357/product/media/images/20220312/21/68836360/413993781/6/6_org_zoom.jpg",
            "videos": None,
            "price": 65.83,
            "available_qty": 2,
            "options": None,
            "variants": None,
            "has_only_default_variant": True,
            "reviews": 3,
            "rating": 3.00,
            "shipping_fee": 0.00,
            "weight": None,
            "length": None,
            "width": None,
            "height": None
        }
        for key in target_product:
            self.assertEqual(product[key], target_product[key])

        print(product["description"])
        self.assertIn('<img src="https://cdn.dsmcdn.com/ty359/product/media/html-images/20220312/18/260796603/8507992c-cf90-4da7-a2c2-1c8959944fcc.jpg">', product["description"])
        StandardProduct(**prod1)

    def test_available_product_8(self):
        url = "https://www.trendyol.com/denthauz/sensetive-ekstra-yumusak-oral-b-uyumlu-dis-fircasi-basligi-4-adet-yedek-baslik-p-791519286"
        with open("trendyol_test/pages/Denthauz Sensetive - Ekstra Yumuşak Oral-B Uyumlu Diş Fırçası Başlığı - 4 Adet Yedek Başlık Fiyatı, Yorumları - Trendyol.html", "rb") as file:
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

        url2 = "https://apigw.trendyol.com/discovery-web-productgw-service/api/product-detail/791519286/html-content?channelId=1"
        with open("trendyol_test/pages/791519286.json", "rb") as file2:
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
            "product_id": "791519286",
            "existence": True,
            "title": "Sensetive - Ekstra Yumuşak Oral-B Uyumlu Diş Fırçası Başlığı - 4 Adet Yedek Başlık",
            "sku": "791519286",
            "upc": "0783191877162",
            "brand": "Denthauz",
            "specifications": [
                {
                    "name": "Paket İçeriği",
                    "value": "4'lü"
                },
                {
                    "name": "Kullanım Amacı",
                    "value": "Komple Ağız Temizliği"
                }
            ],
            "categories": "Kozmetik > Ağız Bakım",
            "images": "https://cdn.dsmcdn.com/ty1440/product/media/images/prod/QC/20240725/15/e900faaa-7283-3e8e-a2a6-d7a8410679bf/1_org_zoom.jpg;https://cdn.dsmcdn.com/ty1440/product/media/images/prod/QC/20240725/15/a72441c4-8b2c-3e67-b17b-89f7d013791b/1_org_zoom.jpg;https://cdn.dsmcdn.com/ty1440/product/media/images/prod/QC/20240725/15/7179a849-583c-3297-bb9d-f2440a9c253f/1_org_zoom.jpg;https://cdn.dsmcdn.com/ty1442/product/media/images/prod/QC/20240725/15/43f60bdb-6cdb-37cf-9650-c47900864cb3/1_org_zoom.jpg;https://cdn.dsmcdn.com/ty1440/product/media/images/prod/QC/20240725/15/d738dda6-004f-3281-811d-148299893ee1/1_org_zoom.jpg",
            "videos": None,
            "price": 5.82,
            "available_qty": None,
            "options": None,
            "variants": None,
            "has_only_default_variant": True,
            "reviews": 22,
            "rating": 4.68,
            "shipping_fee": 0.00,
            "weight": None,
            "length": None,
            "width": None,
            "height": None
        }
        for key in target_product:
            self.assertEqual(product[key], target_product[key])

        print(product["description"])
        self.assertNotIn('</a>', product["description"])
        StandardProduct(**prod1)

    def test_unavailable_product(self):
        url = "https://www.trendyol.com/panterdent/dis-beyazlatici-parlak-set-p-844126911"
        with open("trendyol_test/pages/panterdent Diş Beyazlatıcı Parlak - Set Fiyatı, Yorumları - Trendyol.html", "rb") as file:
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

        url2 = "https://apigw.trendyol.com/discovery-web-productgw-service/api/product-detail/844126911/html-content?channelId=1"
        with open("trendyol_test/pages/844126911.json", "rb") as file2:
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
            "product_id": "844126911",
            "existence": False,
            "title": "Diş Beyazlatıcı Parlak - Set",
            "sku": "844126911",
            "upc": "526598505",
            "brand": "panterdent",
            "specifications": [{
                "name": "Form",
                "value": "Beyazlatma Seti"
            }],
            "categories": "Kozmetik > Ağız Bakım",
            "images": "https://cdn.dsmcdn.com/ty1521/product/media/images/prod/QC/20240903/21/64121aeb-8c39-3197-9155-6a8fca3c5ee7/1_org_zoom.jpg;https://cdn.dsmcdn.com/ty1523/product/media/images/prod/QC/20240903/21/483f9287-8acd-315c-ad35-9cd5d0845b8c/1_org_zoom.jpg;https://cdn.dsmcdn.com/ty1523/product/media/images/prod/QC/20240903/21/355987db-83b6-35d8-8b1b-087e8fabec3e/1_org_zoom.jpg;https://cdn.dsmcdn.com/ty1523/product/media/images/prod/QC/20240903/21/786a87ba-247e-3957-909b-d1087f22725d/1_org_zoom.jpg;https://cdn.dsmcdn.com/ty1521/product/media/images/prod/QC/20240903/21/53a8e389-a54a-332c-b288-a7dbeed8d632/1_org_zoom.jpg",
            "videos": None,
            "price": 46.51,
            "available_qty": 0,
            "options": None,
            "variants": None,
            "has_only_default_variant": True,
            "reviews": 4,
            "rating": 5.00,
            "shipping_fee": 0.00,
            "weight": None,
            "length": None,
            "width": None,
            "height": None,
        }
        for key in target_product:
            self.assertEqual(product[key], target_product[key])

        print(product["description"])
        StandardProduct(**product)


if __name__ == '__main__':
    unittest.main()
