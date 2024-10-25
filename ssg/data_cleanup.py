import json
import os


DESCR_IMG_FILTERS = ['배너', '%EB%B0%B0%EB%84%88', '/common/', '/top_banner', '/promotion', '/brand', '/return', '/notice', '/ulfine']
DESCR_TXT_FILTERS = ['ssg.com', '저작권', 'copyright']


# TODO：净化描述、解析重量


def main():
    old_data = "ssg_products.txt"
    new_data = "ssg_products_temp"

    if os.path.exists(old_data):
        with open(old_data, 'r', encoding='utf-8') as f_old, open(new_data, 'w', encoding='utf-8') as f_new:
            for i, ol in enumerate(f_old, start=1):
                print(f"\nCleanup {i:_}")

                dat = json.loads(ol[:-2])
                descr_temp = dat["description_en"]
                specs = dat['specifications']


    else:
        print("Old data file not found:", old_data)

if __name__ == '__main__':
    main()
