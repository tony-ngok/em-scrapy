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
        result = list(self.spider.parse(response, "Vitamins & Supplements;By Condition;Arthritis & Joints", 280.0))
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
            "categories": "Vitamins & Supplements > By Condition > Arthritis & Joints",
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
        result = list(self.spider.parse(response, "Personal Care & Beauty;Family Planning;Pregnancy Kits", 106.0))
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
            "categories": "Personal Care & Beauty > Family Planning > Pregnancy Kits",
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

        self.assertNotIn('</a>', product['description'])
        self.assertNotIn('</script>', product['description'])
        self.assertNotIn('online in Australia from Pharmacy Online', product['description'])
        self.assertIn('<h1>Product Description & Features</h1>', product['description'])
        self.assertNotIn('<h1>Directions For Use</h1>', product['description'])
        self.assertNotIn('<h1>Ingredients/Material</h1>', product['description'])
        self.assertIn('<h1>Warnings and Disclaimers</h1>', product['description'])

    def test_available_product_3(self):
        url = "https://www.pharmacyonline.com.au/clearblue-rapid-detection-pregnancy-test-1-pack"
        with open("pharmacyonline_test/pages/Clearblue Rapid Detection Pregnancy Test 1 Pack - Buy Online in Australia - Pharmacy Online.html", "rb") as file:
            body = file.read()

        response = HtmlResponse(
            url=url,
            body=body,
        )
        result = list(self.spider.parse(response, "Personal Care & Beauty;Family Planning;Pregnancy Kits", 20.0))
        self.assertEqual(len(result), 1)
        product = result[0]

        target_product = {
            "url": url,
            "product_id": "387460",
            "existence": True,
            "title": "Clearblue Rapid Detection Pregnancy Test 1 Pack",
            "sku": "387460",
            "upc": "4987176009494",
            "brand": "Clearblue",
            "categories": "Personal Care & Beauty > Family Planning > Pregnancy Kits",
            "images": "https://www.pharmacyonline.com.au/media/catalog/product/p/r/proc_4987176009494-0.jpg;https://www.pharmacyonline.com.au/media/catalog/product/p/r/proc_4987176009494-2.jpg;https://www.pharmacyonline.com.au/media/catalog/product/h/q/hqdefault_10_26.jpg",
            "videos": None,
            "price": 4.58,
            "available_qty": None,
            "reviews": 0,
            "rating": 0.00,
            "shipping_fee": 6.56,
            "weight": 0.04
        }
        for key in target_product:
            self.assertEqual(product[key], target_product[key])

        self.assertNotIn('</a>', product['description'])
        self.assertNotIn('</script>', product['description'])
        self.assertNotIn('online in Australia from Pharmacy Online', product['description'])
        self.assertIn('<h1>Product Description & Features</h1>', product['description'])
        self.assertIn('<h1>Directions For Use</h1>', product['description'])
        self.assertNotIn('<h1>Ingredients/Material</h1>', product['description'])
        self.assertIn('<h1>Warnings and Disclaimers</h1>', product['description'])

    def test_available_product_4(self):
        url = "https://www.pharmacyonline.com.au/boost-lab-retinol-night-renewal-serum-30ml"
        with open("pharmacyonline_test/pages/Boost Lab Retinol Night Renewal Serum 30ml - Buy Online in Australia - Pharmacy Online.html", "rb") as file:
            body = file.read()

        response = HtmlResponse(
            url=url,
            body=body,
        )
        result = list(self.spider.parse(response, "Personal Care & Beauty;Skin Care", 100.0))
        self.assertEqual(len(result), 1)
        product = result[0]

        target_product = {
            "url": url,
            "product_id": "10008208",
            "existence": True,
            "title": "Boost Lab Retinol Night Renewal Serum 30ml",
            "sku": "10008208",
            "upc": "9355910000048",
            "brand": "Boost Lab",
            "categories": "Personal Care & Beauty > Skin Care",
            "images": "https://www.pharmacyonline.com.au/media/catalog/product/b/o/boost_lab_retinol_night_renewal_serum_30ml.jpg;https://www.pharmacyonline.com.au/media/catalog/product/b/o/boost_lab_retinol_night_renewal_serum_30ml-1.jpg",
            "videos": None,
            "price": 15.12,
            "available_qty": None,
            "reviews": 0,
            "rating": 0.00,
            "shipping_fee": 6.56,
            "weight": 0.22
        }
        for key in target_product:
            self.assertEqual(product[key], target_product[key])

        self.assertNotIn('</a>', product['description'])
        self.assertNotIn('</script>', product['description'])
        self.assertNotIn('online in Australia from Pharmacy Online', product['description'])
        self.assertIn('<h1>Product Description & Features</h1>', product['description'])
        self.assertIn('<h1>Directions For Use</h1>', product['description'])
        self.assertIn('<h1>Ingredients/Material</h1>', product['description'])
        self.assertIn('<h1>Warnings and Disclaimers</h1>', product['description'])

    def test_unavailable_product_1(self):
        url = "https://www.pharmacyonline.com.au/finishing-touch-flawless-legs-white"
        with open("pharmacyonline_test/pages/Finishing Touch Flawless Legs - Buy Online in Australia - Pharmacy Online.html", "rb") as file:
            body = file.read()

        response = HtmlResponse(
            url=url,
            body=body,
        )
        result = list(self.spider.parse(response, 'Personal Care & Beauty;Waxing & Hair Removal', 354.0))
        self.assertEqual(len(result), 1)
        product = result[0]

        target_product = {
            "url": url,
            "product_id": "10006641",
            "existence": False,
            "title": "Finishing Touch Flawless Legs",
            "sku": "10006641",
            "upc": "0754502038893",
            "brand": "Finishing Touch Flawless",
            "categories": "Personal Care & Beauty > Waxing & Hair Removal",
            "images": "https://www.pharmacyonline.com.au/media/catalog/product/c/h/chur-754502038893-0.jpg;https://www.pharmacyonline.com.au/media/catalog/product/c/h/chur-754502038893-2.jpg",
            "videos": "https://youtu.be/B1mVptPut4o",
            "price": 79.04,
            "available_qty": 0,
            "reviews": 0,
            "rating": 0.00,
            "shipping_fee": 6.56,
            "weight": 0.78
        }
        for key in target_product:
            self.assertEqual(product[key], target_product[key])

        self.assertNotIn('</a>', product['description'])
        self.assertNotIn('</script>', product['description'])
        self.assertNotIn('online in Australia from Pharmacy Online', product['description'])
        self.assertIn('<h1>Product Description & Features</h1>', product['description'])
        self.assertNotIn('<h1>Directions For Use</h1>', product['description'])
        self.assertNotIn('<h1>Ingredients/Material</h1>', product['description'])
        self.assertNotIn('<h1>Warnings and Disclaimers</h1>', product['description'])

    def test_unavailable_product_2(self):
        url = "https://www.pharmacyonline.com.au/neutrogena-oil-free-acne-wash-daily-scrub-125ml"
        with open("pharmacyonline_test/pages/Neutrogena Oil-Free Acne Wash Daily Scrub 125ml - Buy Online in Australia - Pharmacy Online.html", "rb") as file:
            body = file.read()

        response = HtmlResponse(
            url=url,
            body=body,
        )
        result = list(self.spider.parse(response, 'Skin Care;Cleansers & Toners;Foam Cleansers', 155.0))
        self.assertEqual(len(result), 1)
        product = result[0]

        target_product = {
            "url": url,
            "product_id": "242950",
            "existence": False,
            "title": "Neutrogena Oil-Free Acne Wash Daily Scrub 125ml",
            "sku": "242950",
            "upc": "062600300973",
            "brand": "Neutrogena",
            "categories": "Skin Care > Cleansers & Toners > Foam Cleansers",
            "images": "https://www.pharmacyonline.com.au/media/catalog/product/6/2/62600300973.jpg;https://www.pharmacyonline.com.au/media/catalog/product/6/2/62600300973-1.jpg",
            "videos": None,
            "price": 9.55,
            "available_qty": 0,
            "reviews": 79,
            "rating": 4.10,
            "shipping_fee": 6.56,
            "weight": 0.34
        }
        for key in target_product:
            self.assertEqual(product[key], target_product[key])

        self.assertNotIn('</a>', product['description'])
        self.assertNotIn('</script>', product['description'])
        self.assertNotIn('online in Australia from Pharmacy Online', product['description'])
        self.assertIn('<h1>Product Description & Features</h1>', product['description'])
        self.assertIn('<h1>Directions For Use</h1>', product['description'])
        self.assertIn('<h1>Ingredients/Material</h1>', product['description'])
        self.assertNotIn('<h1>Warnings and Disclaimers</h1>', product['description'])

    def test_unavailable_product_3(self):
        url = "https://www.pharmacyonline.com.au/forelife-ovulation-test-x-7"
        with open("pharmacyonline_test/pages/Forelife! Ovulation Test X 7 - Buy Online in Australia - Pharmacy Online.html", "rb") as file:
            body = file.read()

        response = HtmlResponse(
            url=url,
            body=body,
        )
        result = list(self.spider.parse(response, 'Personal Care & Beauty;Family Planning;Ovulation Kits', 130.0))
        self.assertEqual(len(result), 1)
        product = result[0]

        target_product = {
            "url": url,
            "product_id": "681504",
            "existence": False,
            "title": "Forelife! Ovulation Test X 7",
            "sku": "681504",
            "upc": "9324594000255",
            "brand": "Forelife!",
            "categories": "Personal Care & Beauty > Family Planning > Ovulation Kits",
            "images": "https://www.pharmacyonline.com.au/media/catalog/product/f/o/forelife-ultra-sensitive-in-stream-ovulation-test-x-7-p01.jpg",
            "videos": None,
            "price": 9.55,
            "available_qty": 0,
            "reviews": 0,
            "rating": 0.00,
            "shipping_fee": 6.56,
            "weight": 0.29
        }
        for key in target_product:
            self.assertEqual(product[key], target_product[key])

        self.assertNotIn('</a>', product['description'])
        self.assertNotIn('</script>', product['description'])
        self.assertNotIn('online in Australia from Pharmacy Online', product['description'])
        self.assertIn('<h1>Product Description & Features</h1>', product['description'])
        self.assertIn('<h1>Directions For Use</h1>', product['description'])
        self.assertIn('<h1>Ingredients/Material</h1>', product['description'])
        self.assertNotIn('<h1>Warnings and Disclaimers</h1>', product['description'])


if __name__ == '__main__':
    unittest.main()
