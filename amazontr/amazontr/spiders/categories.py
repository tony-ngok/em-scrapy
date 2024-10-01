import scrapy
from scrapy.http import HtmlResponse


# scrapy crawl amazontr_categories -O amazontr_categories.json
class AmazontrCategories(scrapy.Spider):
    name = "amazontr_categories"
    allowed_domains = ["www.amazon.com.tr"]
    start_urls = [
        "https://www.amazon.com.tr/s?i=beauty&fs=true",
        # "https://www.amazon.com.tr/s?i=hpc&fs=true"
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
            yield scrapy.Request(url, headers=self.headers, meta={ 'actual_url': url }, callback=self.parse)

    def parse(self, response: HtmlResponse):
        actual_url = response.meta['actual_url']
        response.headers

        subcats = response.css('li.s-navigation-indent-2 > span > a')
        if subcats:
            for subcat in subcats:
                cat_name = subcat.css('span::text').get().strip()
                if cat_name == 'Cinsel Sağlık ve Aile Planlaması':
                    continue

                href = subcat.css('::attr(href)').get()
                next_url = 'https://www.amazon.com.tr'+href
                headers = { **self.headers, 'Referer': actual_url }

                yield scrapy.Request(next_url, headers=headers, meta={ 'actual_url': next_url }, callback=self.parse)
        else:
            if response.status >= 400:
                print(response.text)
            else:
                clean_url = actual_url.split('fs=true')[0]+'fs=true'
                yield {
                    "cat_url": clean_url
                }
