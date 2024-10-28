import json
import os
import re


DESCR_IMG_FILTERS = ['배너', '%EB%B0%B0%EB%84%88', '/common/', '/top_banner', '/promotion', '/brand', '/return', '/notice', '/ulfine']
DESCR_TXT_FILTERS = ['ssg.com', '저작권', 'copyright']


def weigh(i: int, dat_line: str):
    print(f"\nWeigh {i:_}".replace("_", "."))

    dat = json.loads(dat_line[:-2])
    descr_temp = dat["description_en"]
    specs = dat['specifications']

    dat['weight'] = None
    dat['length'] = None
    dat['width'] = None
    dat['height'] = None

    if specs:
        for spec in specs:
            th_txt = spec['name']
            if ('용량' in th_txt) or ('중량' in th_txt) or ('무게' in th_txt):
                dat['weight'] = parse_weight(spec['value'].lower())
    
    return dat


def parse_weight(txt: str):
    weight_match = re.findall(r'(\d+(?:\.\d+)?)\s*(g|ml|kg|l)', txt)
    if weight_match:
        if weight_match[1] in {'g', 'ml'}:
            return round(float(weight_match[0])/453.59237, 2)
        elif weight_match[1] in {'kg', 'l'}:
            return round(float(weight_match[0])*2.20462, 2)


def main():
    old_data = "ssg_products.txt"
    new_data = "ssg_products_temp"

    if os.path.exists(old_data):
        with open(old_data, 'r', encoding='utf-8') as f_old, open(new_data, 'w', encoding='utf-8') as f_new:
            for i, line in enumerate(f_old, start=1):
                result = weigh(i, line)
                json.dump(result, f_new, ensure_ascii=False)
                f_new.write(",\n")

        os.remove(old_data)
        os.rename(new_data, old_data)
    else:
        print("Old data file not found:", old_data)

if __name__ == '__main__':
    main()
