import os

import scrapy
from scrapy.http import HtmlResponse


# scrapy crawl ssg_categorie
class SsgCategorie(scrapy.Spider):
    name = "ssg_categorie"
    allowed_domains = ["www.ssg.com"]

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': { # 每发送请求后，先经过中间件返回回答，然后将回答通过回调函数处理
            'ssg.middlewares.SsgCatsErrsMiddleware': 543
        }
    }

    HEADERS = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "de-DE,de;q=0.9,en-GB;q=0.8,en;q=0.7",
        "connection": "keep-alive",
        "dnt": "1",
        "sec-ch-ua": '"Chromium";v="130", "Microsoft Edge";v="130", "Not?A_Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0"
    }

    def __init__(self, start_urls: list[str] = ['https://www.ssg.com/monm/main.ssg'], retry: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = start_urls
        self.retry = retry
        self.output_file = "ssg_categories.txt"

    def start_requests(self):
        for i, url in enumerate(self.start_urls):
            print(f"\n{i+1:_}/{len(self.start_urls):_}".replace("_", "."), url)
            if url == 'https://www.ssg.com/monm/main.ssg':
                yield scrapy.Request(url, headers=self.HEADERS,
                                    meta={ "cookiejar": i },
                                    callback=self.parse_monm)
            else:
                yield scrapy.Request(url, headers=self.HEADERS,
                                    meta={ "cookiejar": i },
                                    callback=self.parse)

    def parse_monm(self, response: HtmlResponse):
        all_cats = response.css('a.mndmoon_topctg_lnk::attr(href)').getall()
        
        for cat in all_cats:
            if 'category' in cat:
                if cat.startswith('https://www.ssg.com'):
                    url = cat
                else:
                    url = 'https://www.ssg.com'+cat

                headers = { **self.HEADERS, 'referer': 'https://www.ssg.com' }
                yield scrapy.Request(url, headers=headers,
                                     meta={ "cookiejar": response.meta["cookiejar"] },
                                     callback=self.parse)
    
    def parse(self, response: HtmlResponse):
        write = False

        sub_cats = response.css('div.cmflt_filbox_cts ul li')
        if not sub_cats: # 这就是子分类
            cat_no = response.request.url.split('ctgId=')[1]
            write = True
        else:
            for sc in sub_cats:
                cat_no = sc.css("a::attr(data-ilparam-value)").get("")
                if "none_child" not in sc.css("::attr(class)"):
                    headers = { **self.HEADERS, 'referer': response.url }
                    yield scrapy.Request('https://www.ssg.com/disp/category.ssg?ctgId='+cat_no,
                                         headers=headers,
                                         meta={ "cookiejar": response.meta["cookiejar"] },
                                         callback=self.parse)
                else:
                    write = True

        if write:
            mode = 'a' if (os.path.exists(self.output_file)) and self.retry else 'w'
            with open(self.output_file, mode, encoding="utf-8") as f_out:
                f_out.write(cat_no+'\n')
