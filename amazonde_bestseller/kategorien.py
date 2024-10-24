import asyncio
from sys import argv

from pyppeteer import launch


class AmazondeBSKategorien:
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
        self.kats = {}
        self.todos = []
        
        if review:
            try:
                with open('amazonde_bestsellers_kategorien.txt', 'r', encoding='utf-8') as f_cats:
                    # 抓取记录
                    for line in f_cats:
                        kat = line.strip()
                        self.kats[kat] = True
            except:
                print("Keine Kategorien: Neustarten")
                for todo in todos:
                    self.todos.append(self.get_kat(todo))

            try:
                with open('amazonde_bestsellers_kategorien_fehler.txt', 'r', encoding='utf-8') as f_errs:
                    for line in f_errs:
                        kat = line.strip()
                        self.todos.append(kat)
            except:
                print("Keine vorigen Fehler")
        else:
            print("Neustarten")
            for todo in todos:
                self.todos.append(self.get_kat(todo))

        print(f"{len(self.kats):_} bestehende Kategorie(n)".replace('_', '.'))
        print(f"{len(self.todos):_} URL(s) zu erledigen".replace('_', '.'))

        self.dones = len(self.kats)
        self.errs = 0

    def count(self):
        print(f"{self.dones:_} bestehende Kategorie(n)".replace('_', '.'))
        print(f"{self.errs:_} Fehler".replace('_', '.'))

    def get_kat(self, url: str):
        return url.split('/', 5)[-1]

    async def beginn(self):
        self.browser = await launch(headless=False)
        self.page = await self.browser.newPage()
        self.page.setDefaultNavigationTimeout(180000)
        await self.page.setViewport({ 'width': 1024, 'height': 768 })
        await self.page.setExtraHTTPHeaders(self.HEADERS)

    async def scrape(self):
        for i, k in enumerate(self.todos, start=1):
            k_url = 'https://www.amazon.de/gp/bestsellers/'+k
            await self.besuchen(k_url, i, len(self.todos))

    async def besuchen(self, k_url: str, i: int, total: int, level: int = 0):
        print('\n' + "  "*level + f"{i:_}/{total:_}".replace("_", "."), k_url)
        kat = self.get_kat(k_url)

        try:
            if kat in self.kats:
                print("Duplikat")
                self.count()
                return

            resp = await self.page.goto(k_url)
            if resp.status >= 400:
                print("Fehler", resp.status, "beim URL:", k_url)
                self.kats[kat] = False
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
            
            treeitems = await self.page.querySelectorAll('div[role="group"] > div')
            sublinks = await self.page.querySelectorAll('div[role="group"] a')
            if len(treeitems) == len(sublinks): # 子分类页面会缺少一个子分类要素
                hrefs = [(await self.page.evaluate(self.GET_ATTR_JS, sublink, 'href')) for sublink in sublinks]
                namen = [(await self.page.evaluate(self.GET_TXT_JS, sublink)) for sublink in sublinks]

                for j, (href, name) in enumerate(zip(hrefs, namen), start=1):
                    filter = False
                    for filt in self.FILTERS:
                        if filt in name.lower():
                            print("Gefiltert:", name)
                            filter = True
                            break

                    if not filter:
                        if '/ref=' in href:
                            href = href.split('/ref=')[0]
                        
                        subk_url = 'https://www.amazon.de'+href
                        await self.besuchen(subk_url, j, len(sublinks), level+1)
            else:
                print("Unterkategorie:", kat)
                self.kats[kat] = True
                self.dones += 1
                self.count()
        except Exception as e:
            print("Fehler beim URL:", k_url, f"({str(e)})")
            self.kats[k_url] = False
            self.errs += 1
            self.count()

    async def fin(self):
        await self.browser.close()

        with open('amazonde_bestsellers_kategorien.txt', 'w', encoding='utf-8') as f_cats, open('amazonde_bestsellers_kategorien_fehler.txt', 'w', encoding='utf-8') as f_errs:
            for k, v in self.kats.items():
                if v:
                    f_cats.write(k+'\n')
                else:
                    f_errs.write(k+'\n')


async def main():
    review = False
    if (len(argv) >= 2) and (argv[1] == '--review'):
        review = True

    todos = [
        'https://www.amazon.de/gp/bestsellers/sports',
        'https://www.amazon.de/gp/bestsellers/toys',
        'https://www.amazon.de/gp/bestsellers/books'
    ]

    bs = AmazondeBSKategorien(review, todos)
    await bs.beginn()
    await bs.scrape()
    await bs.fin()


if __name__ == '__main__':
    asyncio.run(main())
