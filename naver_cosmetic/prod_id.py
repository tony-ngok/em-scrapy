import sys
import time
from random import randint

import requests

from cats_urls import urls1, urls2


class NaverCosmeticProdId:
    HEADERS = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "de-DE,de;q=0.9,en-GB;q=0.8,en;q=0.7",
        "dnt": "1",
        "priority": "u=0, i",
        "referer": "https://shopping.naver.com/",
        "sec-ch-ua": "\"Microsoft Edge\";v=\"129\", \"Not=A?Brand\";v=\"8\", \"Chromium\";v=\"129\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Yeti/1.1; +https://naver.me/spd) Chrome/106.0.5249.0 Safari/537.36"
    }

    def __init__(self, mode: str = 'cosmetic', review: bool = False):
        self.mode = mode

        try:
            with open(f'graphql_ext_{mode}.txt', 'r', encoding='utf-8') as f:
                self.graphql_ext = f.read()
                print("GraphQL extension:", self.graphql_ext)
        except:
            print("Fail to get GraphQL extension!")
            sys.exit(1)

        self.prods_ids = {}
        self.todos = []

        if review:
            try:
                with open(f'naver_{mode}_prods_ids.txt', 'r', encoding='utf-8') as f_prods_ids:
                    for line in f_prods_ids:
                        self.prods_ids[line.strip()] = True
            except:
                print("No existents prod(s) id(s)")
                if mode == 'cosmetic':
                    for url in urls1:
                        self.todos.append(url)
                elif mode == 'logistics':
                    for url in urls2:
                        self.todos.append(url)

            try:
                with open(f'naver_{mode}_prod_ids_errs.txt', 'r', encoding='utf-8') as f_errs:
                    for line in f_errs:
                        self.todos.append(line.strip())
            except:
                print("No prev(s) err(s)")
        else:
            print("Start anew")
            if mode == 'cosmetic':
                for url in urls1:
                    self.todos.append(url)
            elif mode == 'logistics':
                for url in urls2:
                    self.todos.append(url)

        print(f"{len(self.prods_ids):_} existent prod(s) id(s)".replace('_', '.'))
        print(f"{len(self.todos):_} URL(s) todo".replace('_', '.'))

        self.dones = len(self.prods_ids)
        self.errs = 0

    def count(self):
        print(f"{self.dones:_} existent prod(s) id(s)".replace('_', '.'))
        print(f"{self.errs:_} error(s)".replace('_', '.'))

    def get_cat_no(self, url: str):
        if self.mode == 'cosmetic':
            return url.split('CH_')[1]
        elif self.mode == 'logistics':
            return url.split('menu=')[1]

    def pause(self, secs: int):
        for s in range(secs, 0, -1):
            print(f"PAUSE: {s:03d}", end='\r')
            time.sleep(1)

    def get_graphql(self, cat_no: str, page: int = 1, page_size: int = 1000):
        if self.mode == 'cosmetic':
            return f'https://shopping.naver.com/api/shopv/graphql?operationName=FetchPagedLuxuryListItems&variables={{"productParam":{{"subVertical":"COSMETIC","soldOut":false,"deliveries":[""],"sorts":[{{"target":"POPULAR","sortDirection":"DESC"}}],"channelNos":["{cat_no}"]}},"listParam":{{"page":{page},"pageSize":{page_size}}}}}&extensions='+self.graphql_ext
        elif self.mode == 'logistics':
            return f'https://shopping.naver.com/responsive/api/shopv/graphql?operationName=FetchPagedLogisticsProducts&variables={{"productParam":{{"vertical":"LOGISTICS","subVertical":"LOGISTICS","soldOut":false,"menuId":"{cat_no}","sorts":[{{"target":"POPULAR","sortDirection":"DESC"}}],"zipCode":"06236"}},"listParam":{{"page":{page},"pageSize":{page_size}}},"menuId":"{cat_no}","includePriorityProducts":true,"hasOptionFilter":false,"includePromotionProducts":false}}&extensions='+self.graphql_ext

    def scrape(self):
        for i, url in enumerate(self.todos, start=1):
            print()
            cat_no = self.get_cat_no(url)
            self.get_ids(i, cat_no)

    def get_ids(self, i: int, cat_no: str, page: int = 1):
        graph_url = self.get_graphql(cat_no, page)
        print(f"{i}/{len(self.todos)}", graph_url)

        try:
            j = 1
            resp = requests.get(graph_url, headers=self.HEADERS, timeout=300, allow_redirects=False)
            while resp.status_code >= 300:
                print(f"API call fail with status {resp.status_code}: {graph_url} ({j}/10)")
                j += 1
                if j > 10:
                    raise Exception(f"Status {resp.status_code}")
                self.pause(randint(90, 120))
                resp = requests.get(graph_url, headers=self.HEADERS, timeout=300, allow_redirects=False)

            if self.mode == 'cosmetic':
                result = resp.json()['data']['pagedLuxuryListItems']
                items = result.get('items', [])
            elif self.mode == 'logistics':
                result = resp.json()['data']['pagedLogisticsProducts']
                items = result.get('products', [])

            for item in items:
                pid = item['productId']
                if pid not in self.prods_ids:
                    self.prods_ids[pid] = True
                    self.dones += 1

            self.count()
            time.sleep(randint(2000, 4000)/1000.0)

            has_more = result['hasMore']
            if has_more:
                self.get_ids(i, cat_no, page+1)
        except Exception as e:
            print("ERROR:", str(e))

            if self.mode == 'cosmetic':
                self.prods_ids[f'CH_{cat_no}'] = False
            elif self.mode == 'logistics':
                self.prods_ids[f'menu={cat_no}'] = False

            self.errs += 1
            self.count()
            self.pause(randint(90, 120))

    def fin(self):
        with open(f'naver_{self.mode}_prods_ids.txt', 'w', encoding='utf-8') as f_prods_ids, open(f'naver_{self.mode}_prod_ids_errs.txt', 'w', encoding='utf-8') as f_errs:
           for k, v in self.prods_ids.items():
                if v:
                    f_prods_ids.write(k+'\n')
                else:
                    f_errs.write(k+'\n')

        if self.errs:
            sys.exit(1)
        else:
            sys.exit(0)


if __name__ == '__main__':
    if (len(sys.argv) >= 2) and ((sys.argv[1] == 'cosmetic') or (sys.argv[1] == 'logistics')):
        review = False
        if (len(sys.argv) >= 3) and (sys.argv[2] == '--review'):
            review = True

        nc_prods = NaverCosmeticProdId(sys.argv[1], review)
        nc_prods.scrape()
        nc_prods.fin()
