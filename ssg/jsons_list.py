import os
import sys


if __name__ == '__main__':
    try:
        with open("ssg_products.txt", "r", encoding='utf-8') as f, open('json_tmp', "w", encoding='utf-8') as f_temp:
            f_temp.write("[\n")
            for line in f:
                f_temp.write(line)
            f_temp.write("\n]")

        os.remove("ssg_products.txt")
        os.rename('json_tmp', "ssg_products.json")
    except Exception as e:
        print("ERROR:", str(e))
