import asyncio
import re
from sys import argv

from pyppeteer import launch


class AmazonBigCats:
    '''
    先抓取所有大分类的URL
    '''

    GET_ATTR_JS = '(elem, attr) => elem.getAttribute(attr)'

    HEADERS = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "de-DE,de;q=0.9",
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

    def __init__(self, review: bool = False, todos: list = []):
        self.big_cats = {}
        self.todos = [] # 未完成的Amazon卖场连结

        if review:
            try:
                with open('amazon_big_cats.txt', 'r', encoding='utf-8') as f_big_cats:
                    for line in f_big_cats:
                        bc = line.strip()
                        self.big_cats[bc] = True
            except:
                print("No previous big cat(s)")
                for todo in todos:
                    self.todos.append(todo)

            try:
                with open('amazon_big_cats_errs.txt', 'r', encoding='utf-8') as f_big_cats_errs:
                    for line in f_big_cats_errs:
                        bc_err = line.strip()
                        self.todos.append(bc_err)
            except:
                print("No previous error(s)")
        else:
            print("Start anew")
            for todo in todos:
                self.todos.append(todo)

        print(f"{len(self.big_cats):_} existent big categorie(s)".replace('_', '.'))
        print(f"{len(self.todos):_} URL(s) to do".replace('_', '.'))

        self.dones = len(self.big_cats)
        self.errs = 0

    def count(self):
        print(f"{self.dones:_} existent big categorie(s)".replace('_', '.'))
        print(f"{self.errs:_} error(s)".replace('_', '.'))

    def get_code(self, url: str, regex: str):
        '''
        用正规表达式获得编码，以在存储时节省空间
        '''

        re_match = re.findall(regex, url)
        if re_match:
            return re_match[0]

    async def begin(self):
        self.browser = await launch(headless=False)
        self.page = await self.browser.newPage()
        self.page.setDefaultNavigationTimeout(180000)
        await self.page.setViewport({ 'width': 1024, 'height': 768 })
        await self.page.setExtraHTTPHeaders(self.HEADERS)

    async def scrape(self):
        for i, todo in enumerate(self.todos, start=1):
            print("\n"+f"{i}/{len(self.todos)}", todo)

            self.region = self.get_code(todo, r'amazon\.([\w\.]+)')
            if self.region == 'de':
                await self.page.setExtraHTTPHeaders({ "Cookie": "lc-acbde=de_DE" }) # Deutsch erzwingen

            await self.visite(todo)

    async def first_visite(self):
        '''
        初次进入页面
        '''

        if self.region == 'com': # 美国站没有确认按纽，只需刷新一下
            resp = await self.page.reload()
            if resp.status >= 400:
                raise Exception(f"Error {resp.status}")
        else:
            accept = await self.page.querySelector('input#sp-cc-accept')
            if accept:
                await accept.click()
                await asyncio.sleep(0.5)
            dismiss = await self.page.querySelector('input[data-action-type="DISMISS"]')
            if dismiss:
                await dismiss.click()
                await asyncio.sleep(0.5)

    async def visite(self, url: str):
        try:
            resp = await self.page.goto(url)
            if resp.status >= 400:
                raise Exception(f"Error {resp.status}")

            # 初次进入页面
            await self.first_visite()

            deps = await self.page.querySelectorAll('li.a-spacing-micro a.a-color-base')
            for dep in deps:
                href = await self.page.evaluate(self.GET_ATTR_JS, dep, 'href')
                if 'gift-card' in href:
                    continue # 跳过礼品券分类

                cat_code = self.region + '_' + self.get_code(href, r'i=([\w-]+)')
                if cat_code not in self.big_cats:
                    self.big_cats[cat_code] = True
                    self.dones += 1

            self.count()
        except Exception as e:
            print("ERROR:", str(e))
            self.big_cats[url] = ''
            self.errs += 1
            self.count()

    async def fin(self):
        await self.browser.close()

        with open('amazon_big_cats.txt', 'w', encoding='utf-8') as f_big_cats, open('amazonde_big_cats_errs.txt', 'w', encoding='utf-8') as f_errs:
            for k, v in self.big_cats.items():
                if v:
                    f_big_cats.write(k+'\n')
                else:
                    f_errs.write(k+'\n')

async def main():
    review = False
    if (len(argv) >= 2) and (argv[1] == '--review'):
        review = True

    # 以下链接皆为各卖场的全分类页面
    todos = [
        'https://www.amazon.com/b?ie=UTF8&node=17602470011',
        'https://www.amazon.co.uk/b?ie=UTF8&node=21579505031',
        'https://www.amazon.de/b?ie=UTF8&node=95045811031'
    ]

    abc = AmazonBigCats(review, todos)
    await abc.begin()
    await abc.scrape()
    await abc.fin()


if __name__ == '__main__':
    asyncio.run(main())
