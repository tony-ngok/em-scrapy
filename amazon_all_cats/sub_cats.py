import asyncio

from pyppeteer import launch


class AmazonBigCats:
    '''
    先抓取所有大分类的URL
    '''

    GET_ATTR_JS = '(elem, attr) => elem.getAttribute(attr)'
    GET_TXT_JS = '(elem) => elem.textContent'

    HEADERS = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "de-DE,de;q=0.9",
        # "Cookie": "lc-acbde=de_DE",
        # "Referer": "https://www.amazon.de/",
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
        
        print(f"{len(self.big_cats):_} existent big categorie(s)".replace('_', '.'))
        print(f"{len(self.todos):_} URL(s) to do".replace('_', '.'))
        
        self.dones = len(self.big_cats)
        self.errs = 0

    def count(self):
        print(f"{self.dones:_} existent big categorie(s)".replace('_', '.'))
        print(f"{self.errs:_} error(s)".replace('_', '.'))
    
    async def begin(self):
        self.browser = await launch(headless=False)
        self.page = await self.browser.newPage()
        self.page.setDefaultNavigationTimeout(180000)
        await self.page.setViewport({ 'width': 1024, 'height': 768 })
        await self.page.setExtraHTTPHeaders(self.HEADERS)
