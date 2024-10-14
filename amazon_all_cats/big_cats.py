import asyncio
import re
from sys import argv

from pyppeteer import launch
from pyppeteer.element_handle import ElementHandle


class AmazonBigCats:
    '''
    先抓取所有大分类的URL
    '''

    GET_ATTR_JS = '(elem, attr) => elem.getAttribute(attr)'
    GET_TXT_JS = '(elem) => elem.textContent'
    GET_TYPE_JS = '(elem) => elem.tagName.toLowerCase()'

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
            for todo in todos:
                self.todos.append(todo)
        
        print(f"{len(self.big_cats):_} existent big categorie(s)".replace('_', '.'))
        print(f"{len(self.todos):_} URL(s) to do".replace('_', '.'))
        
        self.dones = len(self.big_cats)
        self.errs = 0

    def count(self):
        print(f"{self.dones:_} existent big categorie(s)".replace('_', '.'))
        print(f"{self.errs:_} error(s)".replace('_', '.'))
    
    def get_catno(self, url):
        catno_match = re.findall(r'node=(\d+)', url)
        if catno_match:
            return catno_match[0]

    async def begin(self):
        self.browser = await launch(headless=False)
        self.page = await self.browser.newPage()
        self.page.setDefaultNavigationTimeout(180000)
        await self.page.setViewport({ 'width': 1024, 'height': 768 })
        await self.page.setExtraHTTPHeaders(self.HEADERS)

    async def scrape(self):
        for i, todo in enumerate(self.todos, start=1):
            print("\n"+f"{i}/{len(self.todos)}", todo)

            self.region = todo.split('.')[-1]
            if self.region == 'com':
                self.region = 'us'
            if self.region == 'de':
                await self.page.setExtraHTTPHeaders({ "Cookie": "lc-acbde=de_DE" })

            await self.visite(todo)
    
    async def click_elem(self, selector: str | ElementHandle, wait: float = 0.5):
        if isinstance(selector, str):
            elem = await self.page.querySelector(selector)
        else:
            elem = selector

        if elem:
            await elem.click()
            await asyncio.sleep(wait)

    async def visite(self, url: str):
        try:
            resp = await self.page.goto(url+'/ref=nav_bb_logo')
            if resp.status >= 400:
                raise Exception(f"Error {resp.status}")

            # 初次进入页面
            await self.click_elem('input#sp-cc-accept')
            await self.click_elem('input[data-action-type="DISMISS"]')

            await self.click_elem('a#nav-hamburger-menu', 1)
            await self.collect_cats1()
            await self.get_big_cats()
        except Exception as e:
            print("ERROR:", str(e))
            self.big_cats[url] = ''
            self.errs += 1
            self.count()

    async def collect_cats1(self):
        '''
        获得本卖场所有最上级分类按纽
        '''

        menu_sels = await self.page.querySelectorAll('ul.hmenu-visible > li, ul.hmenu-visible > ul')
        if not menu_sels:
            return

        self.cats1_btns = [] # 最上级分类按钮
        self.more_cats = None

        collect_cats = False # 收集分类进行状态
        for ms in menu_sels:
            tag = await self.page.evaluate(self.GET_TYPE_JS, ms)

            if tag == 'li': # li包含卖场所有最上级分类
                ms_child = await ms.querySelector(":scope > div, :scope > a")

                if ms_child:
                    ms_child_tag = await self.page.evaluate(self.GET_TYPE_JS, ms_child)

                    if ms_child_tag == 'div': # 标题
                        ms_txt = (await self.page.evaluate(self.GET_TXT_JS, ms)).strip()
                        if (ms_txt == 'Shop by Department') or (ms_txt == 'Alle Kategorien'): # 开始获得分类
                            collect_cats = True
                    else: # a类连结按纽
                        ms_classes = await self.page.evaluate(self.GET_ATTR_JS, ms_child, 'class')
                        if collect_cats:
                            if ('hmenu-compressed-btn' not in ms_classes):
                                self.cats1_btns.append(ms_child)
                            else: # 本卖场的展开分类按纽
                                self.more_cats = ms_child
                elif collect_cats and ((await self.page.evaluate(self.GET_ATTR_JS, ms, 'class')) == 'hmenu-separator'): # 分界线
                    break # 结束获得分类
            else: # ul展开继续收集
                if collect_cats: 
                    more_cats1 = await ms.querySelectorAll('li > a')
                    for mc1 in more_cats1:
                        self.cats1_btns.append(mc1)

    async def get_big_cats(self):
        """
        获得所有大分类连结号
        """

        await self.click_elem(self.more_cats, 1)

        for c1 in self.cats1_btns:
            print(await self.page.evaluate(self.GET_TXT_JS, c1))
            await self.click_elem(c1)

            back_btn = await self.page.querySelector('a.hmenu-back-button')
            cats2 = (await self.page.querySelectorAll('ul.hmenu-translateX a.hmenu-item'))[2:]
            for c2 in cats2:
                href = await self.page.evaluate(self.GET_ATTR_JS, c2, 'href')
                if 'node=' in href:
                    big_cat_no = self.get_catno(href)

                    if big_cat_no not in self.big_cats:
                        self.big_cats[big_cat_no] = True
                        self.dones += 1
            
            self.count()
            print(self.big_cats.keys())
            await self.click_elem(back_btn, 1)


async def main():
    review = False
    if (len(argv) >= 2) and (argv[1] == '--review'):
        review = True

    todos = [
        'https://www.amazon.com',
        # 'https://www.amazon.co.uk',
        # 'https://www.amazon.de'
    ]

    abc = AmazonBigCats(review, todos)
    await abc.begin()
    await abc.scrape()
    # await abc.fin()


if __name__ == '__main__':
    asyncio.run(main())
