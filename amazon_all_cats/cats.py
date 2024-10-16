import asyncio
import json
import re
from sys import argv

from pyppeteer import launch


class AmazonCats:
    GET_ATTR_JS = '(elem, attr) => elem.getAttribute(attr)'
    GET_TXT_JS = '(elem) => elem.textContent'

    FILTERS = ['eroti', 'lgbt', 'porn', 'prostitu', 'lesb', 'schwul', 'sexu', 'sex &', 'gender studies', 'genderstudies', 'queer']

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
        self.cats = {}
        self.todos = [] # 未完成的Amazon卖场连结

        if review:
            try:
                with open('amazon_cats.json', 'r', encoding='utf-8') as f_cats:
                    for rec in json.load(f_cats):
                        cat_code = self.url_to_code(rec['url'])
                        self.cats[cat_code] = (rec['name'], rec['qty'])
            except:
                print("No previous subcat(s)")
                for todo in todos:
                    self.todos.append(todo)

            try:
                with open('amazon_cats_errs.txt', 'r', encoding='utf-8') as f_cats_errs:
                    for line in f_cats_errs:
                        cat_err = line.strip()
                        self.todos.append(cat_err)
            except:
                print("No previous error(s)")
        else:
            print("Start anew")
            for todo in todos:
                self.todos.append(todo)

        print(f"{len(self.cats):_} existent subcategorie(s)".replace('_', '.'))
        print(f"{len(self.todos):_} URL(s) to do".replace('_', '.'))

        self.dones = len(self.cats)
        self.errs = 0

    def count(self):
        print(f"{self.dones:_} existent subcategorie(s)".replace('_', '.'))
        print(f"{self.errs:_} error(s)".replace('_', '.'))

    def get_code(self, url: str, regex: str):
        '''
        用正规表达式获得编码，以在存储时节省空间
        '''

        re_match = re.findall(regex, url)
        if re_match:
            return re_match[0]

    def url_to_code(self, url: str):
        if 'rh=' in url:
            reg, catno = self.get_code(url, r'amazon\.([\w\.]+).*n%3A(\d+)')
            return f'{reg}:{catno}'
        elif 'i=' in url: # 大分类URL
            reg, catno = self.get_code(url, r'amazon\.([\w\.]+)/s\?i=([\w\-]+)')
            return f'{reg}_{catno}'

    def code_to_url(self, code: str):
        if ':' in code:
            reg, catno = code.split(':')
            return f'https://www.amazon.{reg}/s?rh=n%3A{catno}&fs=true'
        elif '_' in code:
            reg, catno = code.split('_')
            return f'https://www.amazon.{reg}/s?i={catno}&fs=true'

    async def begin(self):
        self.browser = await launch(headless=False)
        self.page = await self.browser.newPage()
        self.page.setDefaultNavigationTimeout(180000)
        await self.page.setViewport({ 'width': 1024, 'height': 768 })
        await self.page.setExtraHTTPHeaders(self.HEADERS)

    async def scrape(self):
        for i, todo in enumerate(self.todos, start=1):
            url = self.code_to_url(todo)

            headers = { **self.HEADERS, 'Referer': url.rsplit('/', 1)[0]+'/' }
            if '.de' in url:
                headers = { **headers, "Cookie": "lc-acbde=de_DE" } # Deutsch erzwingen
            await self.page.setExtraHTTPHeaders(headers)

            await self.visite(url, i, len(self.todos), first=True)

    async def first_visite(self):
        '''
        初次进入页面
        '''

        accept = await self.page.querySelector('input#sp-cc-accept')
        if accept:
            await accept.click()
            await asyncio.sleep(0.5)
        dismiss = await self.page.querySelector('input[data-action-type="DISMISS"]')
        if dismiss:
            await dismiss.click()
            await asyncio.sleep(0.5)

    async def visite(self, url: str, i: int, i_max: int, level: int = 0, cat_name: str = '', first: bool = False):
        print("\n" + "  "*level + f"{i}/{i_max}".replace('_', '.'), url)

        cat_code = self.url_to_code(url)
        if cat_code in self.cats:
            print("Duplicate")
            self.count()
            return

        try:
            resp = await self.page.goto(url)
            # print(resp.request.headers)
            if resp.status >= 400:
                raise Exception(f"Error {resp.status}")

            # 初次进入页面
            if first:
                await self.first_visite()

            # https://www.amazon.com/s?i=dvd&fs=true（stripbooks之后，UK之前）下漏了2个子分类
            sub_cats = await self.page.querySelectorAll('li.s-navigation-indent-2 a')
            if sub_cats:
                print("  "*level + f"{len(sub_cats)} subcategorie(s)")

                sub_names = [(await self.page.evaluate(self.GET_TXT_JS, (await sc.querySelector('span')))) for sc in sub_cats]
                sub_hrefs = [(await self.page.evaluate(self.GET_ATTR_JS, sc, 'href')) for sc in sub_cats]

                for j, (sn, sh) in enumerate(zip(sub_names, sub_hrefs), start=1):
                    filt = False
                    for f in self.FILTERS:
                        if f in sn.lower():
                            filt = True
                            print('Category filtered:', sn)
                            break

                    if not filt:
                        code = re.findall(r'n%3A(\d+)', sh)[-1]
                        await self.visite(url.rsplit('/', 1)[0]+f'/s?rh=n%3A{code}&fs=true', j, len(sub_cats), level+1, sn)
            else: # 翻到子分类了
                subcat_sel = await self.page.querySelector('li.s-navigation-indent-1 > span > span')
                if subcat_sel:
                    cat_name = await self.page.evaluate(self.GET_TXT_JS, subcat_sel)
                elif not cat_name:
                    return

                qty = 0
                qty_sel = await self.page.querySelector('span[data-component-type="s-result-info-bar"] div.sg-col-inner > div > span')
                if qty_sel:
                    qty_txt = (await self.page.evaluate(self.GET_TXT_JS, qty_sel)).split()[-2]
                    qty = int(qty_txt.replace(',', '').replace('.', ''))

                print("Subcategory:", cat_name, f"({qty:_} result(s))".replace('_', '.'))
                self.cats[cat_code] = (cat_name, qty)
                self.dones += 1
                self.count()
        except Exception as e:
            print("ERROR:", str(e))
            self.cats[cat_code] = None
            self.errs += 1
            self.count()

    async def fin(self):
        await self.browser.close()

        with open('amazon_cats.json', 'w', encoding='utf-8') as f_cats, open('amazonde_cats_errs.txt', 'w', encoding='utf-8') as f_errs:
            f_cats.write('[\n')

            writ = False
            for k, v in self.cats.items():
                if v and isinstance(v, tuple):
                    if not writ:
                        writ = True
                    else:
                        f_cats.write(',\n')

                    f_cats.write(f'{{"url": "{self.code_to_url(k)}", "name": "{v[0]}", "qty": {v[1]}}}')
                else:
                    f_errs.write(k+'\n')

            f_cats.write("\n]")

async def main():
    review = False
    if (len(argv) >= 2) and (argv[1] == '--review'):
        review = True

    todos = []
    with open('amazon_big_cats.txt', 'r', encoding='utf-8') as f_big_cats:
        for line in f_big_cats:
            cat_code = line.strip()
            todos.append(cat_code)

    abc = AmazonCats(review, todos)
    await abc.begin()
    await abc.scrape()
    await abc.fin()


if __name__ == '__main__':
    asyncio.run(main())
