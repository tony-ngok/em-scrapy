import json

from pyppeteer import launch


class AmazondeBSKategorien:
    GET_ATTR_JS = '(elem, attr) => elem.getAttribute(attr)'
    GET_TXT_JS = '(elem) => elem.textContent'

    HEADERS = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
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

    def __init__(self, review: bool = False, todo: list = []) -> None:
        if review:
            try:
                with open('amazonde_bestsellers_kategorien.json', 'r', encoding='utf-8') as f_cats: 
                    self.cats_list = [cat['cat_url'] for cat in json.load(f_cats)] # 已经获得的分类页面
                    self.cats_set = set([self.get_catno(url) for url in self.cats_list]) # 不好直接用url hash（太长了，容易误查重）
            except:
                print("No cats file")
                self.cats_list = []
                self.cats_set = set()
        
            try:
                with open('amazontr_categories_errs.json', 'r', encoding='utf-8') as f_errs: # 前面的出错
                    self.todo_list = [cat['cat_url'] for cat in json.load(f_errs)]
            except:
                print("No prev errs")
                self.todo_list = []

            print(len(self.cats_set), "categorie(s)")
            print(len(self.todo_list), "url(s) to do")
        else:
            print("Start anew")
            self.cats_list = []
            self.cats_set = set()
            self.todo_list = todo

        self.errs_list = []
        self.errs_set = set()
            
