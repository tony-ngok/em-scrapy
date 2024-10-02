import asyncio
import json
import re
from sys import argv

from pyppeteer import launch


class AmazontrAsins:
    GET_ATTR_JS = '(elem, attr) => elem.getAttribute(attr)'
    GET_TXT_JS = '(elem) => elem.textContent'

    HEADERS = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://www.amazon.com.tr/",
        "Sec-CH-UA": '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
        "Sec-CH-UA-Mobile": "?0",
        "Sec-CH-UA-Platform": '"Windows"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
    }

    def __init__(self, review: bool, todo: list = []) -> None:
        if review:
            try:
                with open('amazontr_asins.json', 'r', encoding='utf-8') as f_asins: 
                    self.asins_dict = {asin['asin']: True for asin in json.load(f_asins)} # 已经获得的分类页面
            except:
                print("No asins file")
                self.asins_dict = {}
        
            try:
                with open('amazontr_asins_errs.json', 'r', encoding='utf-8') as f_errs: # 前面的出错
                    self.todo_list = [(cat['cat_url'], cat['from_page']) for cat in json.load(f_errs)]
            except:
                print("No prev errs")
                self.todo_list = []

            print(f"{len(self.asins_dict):_} asin(s)".replace('_', '.'))
            print(len(self.todo_list), "url(s) to do")
        else:
            print("Start anew")
            self.asins_dict = {}
            self.todo_list = todo

        self.errs_dict = {}

    def get_catno(self, url):
        catno_match = re.findall(r'n%3A(\d+)', url)
        if catno_match:
            return catno_match[-1]

    def get_asin(self, url):
        asin_match = re.findall(r'/dp/(\w+)', url)
        if asin_match:
            return asin_match[0]

    async def start(self) -> None:
        self.browser = await launch(headless=False)
        self.page = await self.browser.newPage()
        await self.page.setViewport({ 'width': 1024, 'height': 768 })
        await self.page.setExtraHTTPHeaders(self.HEADERS)
    
    async def scrape(self):
        for url in self.todo_list:
            await self.visite(url[0], url[1])

    async def visite(self, cat_url: str, page_no: int = 1) -> None:
        url = cat_url
        if page_no > 1:
            url += f'&page={page_no}'
        
        try:
            resp = await self.page.goto(url,
                                        # { 'waitUntil': 'networkidle2' }
                                        )
            if (resp.status >= 300):
                print("Error", resp.status)
                self.errs_dict[cat_url] = page_no
                print(f"{len(self.asins_dict):_} asin(s)".replace('_', '.'))
                print(len(self.errs_dict), "error categorie(s)")
                return

            if (await self.page.querySelector('input[id="sp-cc-accept"]')):
                await self.page.click('input[id="sp-cc-accept"]')
                await asyncio.sleep(1)

            print(f'\ncat {self.get_catno(cat_url)} page {page_no}')

            prod_cards = await self.page.querySelectorAll('div[data-cy="title-recipe"]')
            prod_cards = [pc for pc in prod_cards if not await pc.querySelector(':scope a.puis-sponsored-label-text')]
            print(len(prod_cards), 'asin(s) here')

            for pc in prod_cards:
                pc_a = await pc.querySelector(':scope h2 > a')
                href = await self.page.evaluate(self.GET_ATTR_JS, pc_a, 'href')
                asin = self.get_asin(href)
                
                if asin not in self.asins_dict:
                    self.asins_dict[asin] = True
            
            print(f"{len(self.asins_dict):_} asin(s)".replace('_', '.'))
            print(len(self.errs_dict), "error url(s)")

            goto_next = await self.page.querySelector('a.s-pagination-next')
            if goto_next:
                await self.visite(cat_url, page_no+1)
        except Exception as e:
            print("Error:", str(e))
            self.errs_dict[cat_url] = page_no
            print(f"{len(self.asins_dict):_} asin(s)".replace('_', '.'))
            print(len(self.errs_dict), "error url(s)")


async def main():
    review = False
    if (len(argv) >= 2) and argv[1] == '--review':
        review = True

    todo_list = []
    if not review: # 从头开始
        todo_list.append(('https://www.amazon.com.tr/s?rh=n%3A12572036031&fs=true', 1))
        todo_list.append(('https://www.amazon.com.tr/s?rh=n%3A13526710031&fs=true', 1))

    ac = AmazontrAsins(review, todo_list)
    await ac.start()
    await ac.scrape()
    await ac.browser.close()
    
    asins_links = ',\n'.join([f'{{ "asin": "{asin}" }}' for asin in ac.asins_dict])
    with open('amazontr_asins.json', 'w') as f:
        f.write('[\n')
        f.write(asins_links)
        f.write('\n]')
    
    errs_links = ',\n'.join([f'{{ "cat_url": {url}, "from_page": {fp} }}' for url, fp in ac.errs_dict.items()])
    with open('amazontr_asins_errs.json', 'w') as f:
        f.write('[\n')
        f.write(errs_links)
        f.write('\n]')


if __name__ == '__main__':
    asyncio.run(main())
