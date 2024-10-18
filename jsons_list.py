from sys import argv


if __name__ == '__main__':
    try:
        if len(argv) >= 2:
            with open(argv[1], "r+", encoding='utf-8') as f:
                f.write('[\n')
                f.seek(-2, 2)
                f.write('\n]')
    except Exception as e:
        print("ERROR:", str(e))
