import asyncio
import re
from sys import argv

from pyppeteer import launch


class AmazondeBSAsins:
    GET_ATTR_JS = '(elem, attr) => elem.getAttribute(attr)'
    GET_TXT_JS = '(elem) => elem.textContent'

    FILTERS = ['erotik', 'erotisch', 'lesben', 'lesbisch', 'schwul', 'bisexuell', 'transgender', 'genderstudies', 'queer', 'lgbt']

    HEADERS = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "de-DE,de;q=0.9",
        "Cookie": "lc-acbde=de_DE",
        "Referer": "https://www.amazon.de/",
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
        self.asins = {}
        self.todos = []

        if review:
            try:
                with open('amazonde_bestsellers_asins.txt', 'r', encoding='utf-8') as f_asins:
                    for line in f_asins:
                        self.asins[line.strip()] = True
            except:
                print("Keine ASIN-Nummern: Neustarten")
                for todo in todos:
                    self.todos.append(todo)

            try:
                with open('amazonde_bestsellers_asins_fehler.txt', 'r', encoding='utf-8') as f_errs:
                    for line in f_errs:
                        self.todos.append(line.strip())
            except:
                print("Keine vorigen Fehler")
        else:
            print("Neustarten")
            for todo in todos:
                self.todos.append(todo)

        print(f"{len(self.asins):_} bestehende ASIN-Nummer(n)".replace('_', '.'))
        print(f"{len(self.todos):_} URL(s) zu erledigen".replace('_', '.'))

        self.dones = len(self.asins)
        self.errs = 0

    def count(self):
        print(f"{self.dones:_} bestehende ASIN-Nummer(n)".replace('_', '.'))
        print(f"{self.errs:_} Fehler".replace('_', '.'))

    async def beginn(self):
        self.browser = await launch(headless=False)
        self.page = await self.browser.newPage()
        self.page.setDefaultNavigationTimeout(180000)
        await self.page.setViewport({ 'width': 1024, 'height': 768 })
        await self.page.setExtraHTTPHeaders(self.HEADERS)

    async def scrape(self):
        for i, asin in enumerate(self.todos, start=1):
            url = 'https://www.amazon.de/gp/bestsellers/'+asin
            print("\n"+f"{i:_}/{len(self.todos):_}".replace('_', '.'), url)
            await self.besuch(url)

    async def besuch(self, url: str):
        try:
            resp = await self.page.goto(url)
            if resp.status >= 400:
                print("Fehler", resp.status, "beim URL:", url)
                self.asins[url] = False
                self.errs += 1
                self.count()
                return

            # 初次进入网页
            accept = await self.page.querySelector('input#sp-cc-accept')
            if accept:
                await accept.click()
                await asyncio.sleep(0.5)
            dismiss = await self.page.querySelector('input[data-action-type="DISMISS"]')
            if dismiss:
                await dismiss.click()
                await asyncio.sleep(0.5)

            gr_kat = (await self.page.querySelectorAll('div[role="treeitem"] > a'))[2] # 大分类下的第一级子分类
            gr_kat_name = (await self.page.evaluate(self.GET_TXT_JS, gr_kat)).strip()
            if gr_kat_name == 'Erotik':
                print("Kategorie gefiltert: Erotik")
                self.count()
                return

            akt_kat = await self.page.querySelector('div[role="treeitem"] > span')
            akt_kat_name = await self.page.evaluate(self.GET_TXT_JS, akt_kat)
            for filt in self.FILTERS:
                if filt in akt_kat_name.lower():
                    print("Unterkategorie gefiltert:", akt_kat_name)
                    self.count()
                    return

            # 提取ASIN号
            asins_div = await self.page.querySelector('div.p13n-desktop-grid')
            if asins_div:
                asins_daten = await self.page.evaluate(self.GET_ATTR_JS, asins_div, 'data-client-recs-list')
                if asins_daten:
                    # print(asins_daten)
                    asins_match = re.findall(r'"id":"(\w+)"', asins_daten)
                    print(len(asins_match), "ASIN-Nummer(n) auf dieser Seite")
                    if asins_match:
                        for asin in asins_match:
                            if asin not in self.asins:
                                self.asins[asin] = True
                                self.dones += 1
            self.count()

            # 第2页
            seite2 = await self.page.querySelector('li.a-last > a')
            if seite2:
                await self.besuch(url+'?ie=UTF8&pg=2')
        except Exception as e:
            print("Fehler beim URL:", url, f"({str(e)})")
            self.asins[url] = False
            self.errs += 1
            self.count()

    async def fin(self):
        await self.browser.close()

        with open('amazonde_bestsellers_asins.txt', 'w', encoding='utf-8') as f_asins, open('amazonde_bestsellers_asins_fehler.txt', 'w', encoding='utf-8') as f_errs:
            for k, v in self.asins.items():
                if v:
                    f_asins.write(k+'\n')
                else:
                    f_errs.write(k+'\n')


async def main():
    review = False
    if (len(argv) >= 2) and (argv[1] == '--review'):
        review = True

    todos = [
        # 'fashion/27009105031', # 测试用
        # 'books/16381756031',
    ]
    with open('amazonde_bestsellers_kategorien.txt', 'r', encoding='utf-8') as f_cats:
        for kat in f_cats:
            todos.append(kat.strip())

    bs = AmazondeBSAsins(review, todos)
    await bs.beginn()
    await bs.scrape()
    await bs.fin()


if __name__ == '__main__':
    asyncio.run(main())
