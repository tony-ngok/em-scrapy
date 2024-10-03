import scrapy
from scrapy.http import HtmlResponse


# scrapy crawl yahoojp_categories -O yahoojp_categories.json
class YahoojpCategories(scrapy.Spider):
    name = "yahoojp_categories"
    allowed_domains = ['shopping.yahoo.co.jp']
    start_urls = ['https://shopping.yahoo.co.jp/category/2501/recommend?sc_i=shp_pc_top_cate_menu_cosm_and_frag:2501:rcmd']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "fr-FR,fr;q=0.9,en-GB;q=0.8,en;q=0.7",
            "dnt": "1",
            "priority": "u=0, i",
            "sec-ch-ua": '"Microsoft Edge";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            "sec-ch-ua-arch": '"x86"',
            "sec-ch-ua-full-version-list": '"Microsoft Edge";v="129.0.2792.65", "Not=A?Brand";v="8.0.0.0", "Chromium";v="129.0.6668.71"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-model": '""',
            "sec-ch-ua-platform": '"Windows"',
            "sec-ch-ua-platform-version": '"10.0.0"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0"
        }

    def start_requests(self):
        yield scrapy.Request(self.start_urls[0], headers=self.headers, callback=self.parse)

    def parse(self, response: HtmlResponse):
        sub_cats = response.css('li.style_SubCategoryList__subCategoryItem__MdKvA > a')[1:] # 去掉全部商品
        if not sub_cats:
            yield { 'cat_url': response.url.split('?')[0] }
        else:
            for sub_cat in sub_cats:
                headers = { **self.headers, 'referer': response.url }
                yield scrapy.Request(sub_cat.css('::attr(href)').get(),
                                    headers=headers,
                                    callback=self.parse)
