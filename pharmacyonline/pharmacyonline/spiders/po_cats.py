import re

import scrapy
from scrapy.http import HtmlResponse


# scrapy crawl po_cats
class POCategories(scrapy.Spider):
    """
    首页子分类内容为传统HTML，因此可直接用Scrapy抓取
    """

    name = "po_cats"
    allowed_domains = ['www.pharmacyonline.com.au']
    start_urls = ['https://www.pharmacyonline.com.au/']
    cats_output = "po_cats.txt"

    HEADERS = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.8,en-GB;q=0.5,en;q=0.3",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0"
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.retry = False

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, headers=self.HEADERS, callback=self.parse)

    def get_cat_name(self, href: str):
        cat_match = re.findall(r'https://www\.pharmacyonline\.com\.au/(.*)', href)
        if cat_match:
            return cat_match[0]

    def parse(self, response: HtmlResponse):
        lv2x = response.css('li[data-title="Shop by category"] li.-level2')
        for lv2 in lv2x:
            lv2_cat_name = lv2.css('a::attr(title)').get('').strip().lower()
            if lv2_cat_name and (lv2_cat_name != 'prescriptions') and (lv2_cat_name != 'sexual health'):
                lv3x = lv2.css(':scope li.item')
                for lv3 in lv3x:
                    lv3_cat_name = lv3.css('a::attr(title)').get('').strip().lower() # 分类名
                    lv3_classes = lv3.css('::attr(class)').get('') # 判断下面是否有子分类

                    if lv3_cat_name and (not (('sexual' in lv3_cat_name) or ('-parent' in lv3_classes))):
                        cat_no = self.get_cat_name(lv3.css('a::attr(href)').get(''))
                        if cat_no:
                            self.write_cat(cat_no)

    def write_cat(self, cat_no: str):
        mod = 'a' if self.retry else 'w'
        with open(self.cats_output, mod, encoding='utf-8') as f_cats:
            f_cats.write(cat_no+'\n')
        if not self.retry:
            self.retry = True
