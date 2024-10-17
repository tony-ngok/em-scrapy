import math
import sys
import time

import requests


class NaverHandmadeProdId:
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
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0"
    }

    def __init__(self, review: bool = False, todos: list = []):
        self.prods_ids = {}
        self.todos = []

        if review:
            try:
                with open('naver_handmade_prods_ids.txt', 'r', encoding='utf-8') as f_prods_ids:
                    for line in f_prods_ids:
                        self.prods_ids[line.strip()] = True
            except:
                print("No existents prod(s) id(s)")
                for todo in todos:
                    self.todos.append(todo)

            try:
                with open('naver_handmade_prod_ids_errs.txt', 'r', encoding='utf-8') as f_errs:
                    for line in f_errs:
                        self.todos.append(line.strip())
            except:
                print("No prev(s) err(s)")
        else:
            print("Start anew")
            for todo in todos:
                self.todos.append(todo)

        print(f"{len(self.prods_ids):_} existent prod(s) id(s)".replace('_', '.'))
        print(f"{len(self.todos):_} URL(s) todo".replace('_', '.'))

        self.dones = len(self.prods_ids)
        self.errs = 0

    def count(self):
        print(f"{self.dones:_} existent prod(s) id(s)".replace('_', '.'))
        print(f"{self.errs:_} error(s)".replace('_', '.'))

    # Naver API 翻页每个分类最大可以取得1万个商品，每页最多可以有306个商品
    def brand_cat_api(self, cat: str, page: int = 1, page_size: int = 306):
        return f"https://shopping.naver.com/v1/products?_nc_=1729141200000&subVertical=HANDMADE&page={page}&pageSize={page_size}&sort=RECENT&filter=ALL&displayType=CATEGORY_HOME&includeZzim=true&includeViewCount=true&includeStoreCardInfo=true&includeStockQuantity=false&includeBrandInfo=false&includeBrandLogoImage=false&includeRepresentativeReview=false&includeListCardAttribute=false&includeRanking=false&includeRankingByMenus=false&includeStoreCategoryName=false&includeIngredient=false&menuId={cat}&brandIds[]=&standardSizeKeys[]=&standardColorKeys[]=&attributeValueIds[]=&attributeValueIdsAll[]=&certifications[]=&includeStoreInfoWithHighRatingReview=false&guaranteeTypes[]="

    def scrape(self):
        for i, cat in enumerate(self.todos, start=1):
            print()
            self.get_ids(i, cat)

    def get_ids(self, i: int, cat: str, page: int = 1, page_size: int = 306):
        api = self.brand_cat_api(cat, page, page_size)
        print(f"{i}/{len(self.todos)}", api)

        try:
            resp = requests.get(api, headers=self.HEADERS, timeout=300)
            if resp.status_code >= 300:
                raise Exception(f"Status {resp.status_code}")

            result = resp.json()
            products = result['products']
            for p in products:
                pid = p['_id']
                if pid not in self.prods_ids:
                    self.prods_ids[pid] = True
                    self.dones += 1

            self.count()
            time.sleep(1)

            has_more = result['hasMoreProducts']
            if has_more and (page < math.ceil(10000/page_size)):
                self.get_ids(i, cat, page+1, page_size)
        except Exception as e:
            print("ERROR:", str(e))
            self.prods_ids[f"c{cat}"] = False
            self.errs += 1
            self.count()  

    def fin(self):
        with open('naver_handmade_prods_ids.txt', 'w', encoding='utf-8') as f_prods_ids, open('naver_handmade_prod_ids_errs.txt', 'w', encoding='utf-8') as f_errs:
            for k, v in self.prods_ids.items():
                if v:
                    f_prods_ids.write(k+'\n')
                else:
                    f_errs.write(k[1:]+'\n')

        if self.errs:
            sys.exit(1)
        else:
            sys.exit(0)


if __name__ == '__main__':
    review = False
    if (len(sys.argv) >= 2) and (sys.argv[1] == '--review'):
        review = True

    todos = []
    if not review:
        for c in [64, 65, 66, 68, 69, 70, 71]:
            todos.append(f"100048{c}")

    nh_prods = NaverHandmadeProdId(review, todos)
    nh_prods.scrape()
    nh_prods.fin()
