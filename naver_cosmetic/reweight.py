# 从已经抓下来的参数补齐重量字段

import json
import os
import re
import sys


def parse_weight(txt: str):
    weight_match = re.findall(r'(\d+(?:\.\d+)?)\s*(?:g|ml)', txt)
    if weight_match:
        return round(float(weight_match[0])/453.59237, 2)


if __name__ == '__main__':
    if (len(sys.argv) >= 2) or (sys.argv[1] == 'cosmetic') or (sys.argv[1] == 'logistics'):
        try:
            with open(f'naver_{sys.argv[1]}_prods.txt', 'r', encoding='utf-8') as f_orig, open('prods_temp', 'w', encoding='utf-8') as f_new:
                for i, line in enumerate(f_orig, start=1):
                    print("Item", f"{i:_}".replace("_", "."))
                    data = json.loads(line[:-2])
                    specs = data['specifications']

                    for spec in specs:
                        if ('용량' in spec['name']) or ('중량' in spec['name']):
                            print(f"Reweight ({spec['name']})")
                            data['weight'] = parse_weight(spec['value'])
                            print(f"Weight: {data['weight']}".replace(".", ","))
                            break

                    json.dump(data, f_new, ensure_ascii=False)
                    f_new.write(',\n')

            os.remove(f"naver_{sys.argv[1]}_prods.txt")
            os.rename('prods_temp', f"naver_{sys.argv[1]}_prods.txt")
        except Exception as e:
            print("ERROR:", str(e))
