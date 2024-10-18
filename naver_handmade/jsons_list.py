import os


if __name__ == '__main__':
    try:
        with open("naver_handmade_prods.txt", "r", encoding='utf-8') as f:
            with open('json_tmp', "w", encoding='utf-8') as f_temp:
                f_temp.write("[\n")
                f_temp.write(f.read()[:-2])
                f_temp.write("\n]")

        os.remove("naver_handmade_prods.txt")
        os.rename('json_tmp', "naver_handmade_prods.json")
    except Exception as e:
        print("ERROR:", str(e))
