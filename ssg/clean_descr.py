import json
import os
import re

from bs4 import BeautifulSoup
from bs4.element import Comment
from scrapy.http import HtmlResponse


DESCR_IMG_FILTERS = ['%EB%B0%B0%EB%84%88', '/common/', '/top_banner', '/promotion',
                     '/brand', '/return', '/notice', '/ulfine', '/product/000000/', '/note',
                     '/delivery', '%EB%B0%B0%EC%86%A1', '%EB%B0%98%ED%92%88',
                     '%EC%95%88%EB%82%B4', '%EA%B5%90%ED%99%98', '%ED%83%9D%EB%B0%B0',
                     '%EC%BF%A0%ED%8F%B0', '/shipping', '%EA%B3%B5%EC%A7%80', '/gift',
                     '%EA%B8%B0%ED%94%84%ED%8A%B8', '%EC%A0%80%EC%9E%91%EA%B6%8C', '/copyright']
DESCR_TXT_FILTERS = ['ssg.com', '저작권', 'copyright']


def get_descr(soup: str | BeautifulSoup):
    """
    使用BeautifulSoup整理描述
    """

    descr = ""
    if isinstance(soup, str):
        soup = BeautifulSoup(soup, 'html.parser')

    # 遍历所有子要素（包括纯文字）
    for child in soup.children:
        if isinstance(child, Comment):
            continue
        if child.name: # HTML要素
            if (child.name == 'div'):
                descr += get_descr(child)
            elif child.name == 'p':
                p_descr = get_descr(child)
                if p_descr:
                    descr += f'<p>{p_descr}</p>'
            elif child.name not in {'script', 'button', 'a', 'input', 'form', 'link'}:
                child_str = str(child).strip()
                if child_str:
                    filt = False
                    if '<img' in child_str:
                        for f in DESCR_IMG_FILTERS:
                            if f in child_str.lower(): # 过滤掉无用资料的图片
                                filt = True
                                break
                    if not filt:
                        descr += child_str
        elif isinstance(child, str): # 纯文字
            child_strip = child.strip()
            if child_strip:
                txt_filt = False
                for tf in DESCR_TXT_FILTERS: # 过滤掉版权信息等
                    if tf in child_strip.lower():
                        txt_filt = True
                        break
                if not txt_filt:
                    descr += child_strip

    descr = re.sub(r'<a.*</a>', '', descr) # EM描述中不让包含<a>标签
    descr = " ".join(descr.split())
    return descr

def main():
    old_data = "ssg_products.txt"
    new_data = "ssg_products_temp"

    if os.path.exists(old_data):
        with open(old_data, 'r', encoding='utf-8') as f_old, open(new_data, 'w', encoding='utf-8') as f_new:
            for i, line in enumerate(f_old, start=1):
                print(f"\nRedescription {i:_}".replace("_", "."))

                dat = json.loads(line[:-2])
                if (not dat['existence']) and (dat['available_qty']):
                    dat['available_qty'] = 0

                desc_table = dat['description']
                descr = ""

                response = HtmlResponse('', body=dat['description_en'], encoding='utf-8')
                divx = response.css('body > div')
                for div in divx:
                    if div.css('*'):
                        descr_raw = " ".join(div.get().split())
                        descr += get_descr(descr_raw)

                descr = f'<div class="ssg-descr">{descr}</div>' if descr else ""
                dat['description'] = descr+desc_table if descr or desc_table else None
                print(dat['description'])
                dat['description_en'] = None

                json.dump(dat, f_new, ensure_ascii=False)
                f_new.write(",\n")

        os.remove(old_data)
        os.rename(new_data, old_data)
    else:
        print("Old data file not found:", old_data)

if __name__ == '__main__':
    main()
