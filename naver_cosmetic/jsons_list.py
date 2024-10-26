import os
import sys


if __name__ == '__main__':
    if (len(sys.argv) >= 2) and ((sys.argv[1] == 'cosmetic') or (sys.argv[1] == 'logistics')):
        try:
            with open(f"naver_{sys.argv[1]}_prods.txt", "r", encoding='utf-8') as f:
                with open('json_tmp', "w", encoding='utf-8') as f_temp:
                    f_temp.write("[\n")
                    f_temp.write(f.read()[:-2])
                    f_temp.write("\n]")

            os.remove(f"naver_{sys.argv[1]}_prods.txt")
            os.rename('json_tmp', f"naver_{sys.argv[1]}_prods.json")
        except Exception as e:
            print("ERROR:", str(e))
