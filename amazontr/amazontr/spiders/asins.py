import re

import scrapy
from scrapy.http import HtmlResponse


# scrapy crawl amazontr_asins -O amazontr_asins.json
class AmazontrAsins(scrapy.Spider):
    name = "amazontr_asins"
    allowed_domains = ["www.amazon.com.tr"]
    start_urls = [
        "https://www.amazon.com.tr/s?rh=n%3A14102463031&fs=true",
        "https://www.amazon.com.tr/s?rh=n%3A13526965031&fs=true"
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # https://scrapeops.io/python-scrapy-playbook/scrapy-503-service-unavailable-error/#optimize-request-headers
        self.headers = {
            "Connection": 'keep-alive',
            "Cache-Control": 'max-age=0',
            "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
            "sec-ch-ua-mobile": '?0',
            "sec-ch-ua-platform": "macOS",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.83 Safari/537.36',
            "Accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            "Sec-Fetch-Site": 'none',
            "Sec-Fetch-Mode": 'navigate',
            "Sec-Fetch-User": '?1',
            "Sec-Fetch-Dest": 'document',
            "Accept-Encoding": 'gzip, deflate, br',
            "Accept-Language": 'fr-FR,fr;q=0.9,en-GB;q=0.8,en;q=0.7',
            # "Cookie": 'session-id=261-6962176-2121760; session-id-time=2082787201l; i18n-prefs=TRY; ubid-acbtr=262-5292875-4606067; session-token="nIegK7zo9t1XfCjHVM8a9CYvcOAhFZsRH5teq7xpenz6YtCl8y2jxkct5qghACxyr4Q4ciql0OTHifJ5u4qJRG9LpZpCcnLXEn/l+JziGZFJBE18LydgV22smjnPPLcg9KG73bE02bA1EWFFe4ahNMPai9GB0OzWuxYO+ujj/X1EUNotm9/xxezKPiIbxnWrzTtxq6QKCmbIowzkmWLljMGeBefkLRDh2xoJtQ9o5evvHLtsyb5JowxwFVxleSRER3ihl5XiO2TTLX6Xx4gT9Yuf//kggp7VscEmHorDOgBNk7eUY7kbKUk73qu+m/N0ctGYr4gOkIQB57JoHlEtUYM0GMLNbG1BfW1KSg8DAgA="; csm-hit=tb:T3K91DT3W7N8SY6ZN6FK+s-EZD0Y0T9CH2AD4D425Z5|1727815462053&t:1727815462053&adb:adblk_no'
        }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, headers=self.headers,
                                 meta={
                                     'cat_url': url,
                                     'actual_page': 1
                                     },
                                callback=self.parse)

    def parse(self, response: HtmlResponse):
        cat_url = response.meta['cat_url']
        actual_page = response.meta['actual_page']

        if response.status >= 400:
            print(response.text)
            return

        prod_cards = response.css('div[data-cy="title-recipe"]')
        for pc in prod_cards:
            if pc.css(':scope a.puis-sponsored-label-text'):
                continue

            pc_url = pc.css(':scope h2 > a::attr(href)').get()
            asin_match = re.findall(r'/dp/(\w+)', pc_url)
            if asin_match:
                yield { 'asin': asin_match[0] }
        
        if response.css('a.s-pagination-next'):
            headers = { **self.headers, 'Referer': cat_url+f'&page={actual_page}' }
            yield scrapy.Request(cat_url+f'&page={actual_page+1}', headers=headers,
                                 meta={
                                    'cat_url': cat_url,
                                    'actual_page': actual_page+1
                                 },
                                 callback=self.parse)
