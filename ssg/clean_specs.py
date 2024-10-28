import json
import os


def filter_specs(specs: list[dict]):
    cleaned_specs = []

    weight_added = False
    for spec in specs:
        th_txt = spec['name']
        if ('성분' in th_txt) or ('주의사항' in th_txt) or ('방법' in th_txt) or ('기한' in th_txt):
            continue
        if ('용량' in th_txt) and weight_added:
            continue

        cleaned_specs.append(spec)
        if ('용량' in th_txt) or ('중량' in th_txt): # 重量参数不重复
            weight_added = True


def main():
    old_data = "ssg_products.txt"
    new_data = "ssg_products_temp"

    if os.path.exists(old_data):
        with open(old_data, 'r', encoding='utf-8') as f0, open(new_data, 'w', encoding='utf-8') as f1:
            for i, ol in enumerate(f0, start=1):
                print(f"\nRespec {i:_}".replace("_", "."))

                dat = json.loads(ol[:-2])
                old_specs = dat['specifications']
                dat['specifications'] = filter_specs(old_specs)
                print(dat['specifications'])

                json.dump(dat, f1, ensure_ascii=False)
                f1.write(",\n")

        os.remove(old_data)
        os.rename(new_data, old_data)
    else:
        print("Old data file not found:", old_data)

if __name__ == '__main__':
    main()
