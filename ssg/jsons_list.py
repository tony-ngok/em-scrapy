import os
import sys


if __name__ == '__main__':
    try:
        with open(f"ssg_products.txt", "r", encoding='utf-8') as f, open('json_tmp', "w", encoding='utf-8') as f_temp:
            f_temp.write("[\n")
            for line in f:
                f_temp.write(f.read()[:-2])
            f_temp.write("\n]")

        os.remove(f"ssg_products.txt")
        os.rename('json_tmp', f"ssg_products.json")
    except Exception as e:
        print("ERROR:", str(e))
