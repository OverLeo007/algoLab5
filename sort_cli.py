import argparse

import external_two_way_sort as ext


def main():
    """
    Точка входа CLI
    """
    parser = argparse.ArgumentParser(description="Внешняя сортировка "
                                                 "методом двухпутевого сбалансированного слияния")
    parser.add_argument("-src", dest="src", type=str, nargs="+",
                        help="Список исходных файлов")
    parser.add_argument("--output", "-out", dest="output", type=str, default=None,
                        help="Выходной файл")
    parser.add_argument("--type_data", "-td", dest="type_data", type=str, default="i",
                        help="Тип данных считываемых из файла")
    parser.add_argument("--reverse", "-r", dest="reverse", default=False,
                        action=argparse.BooleanOptionalAction,
                        help="Если указано - сортирует по невозрастанию")
    parser.add_argument("-key", dest="key", default=None, type=str,
                        help="Ключ столбца для csv файла")
    parser.add_argument("--delimiter", "-d", dest="delimiter", default=",",
                        help="Разделитель для csv файла")
    args = parser.parse_args()
    res = {"src": args.src,
           "output": args.output,
           "type_data": args.type_data,
           "reverse": args.reverse,
           "key": args.key,
           "delimiter": args.delimiter
           }
    ext.sort(**res)

def for_tests():
    filenames_txt = []
    filenames_csv = []
    for i in range(1, 5):
        ext.external_sort.generate_input(f"input{i}.txt")
        ext.external_sort.generate_csv_input(f"input{i}.csv")
        filenames_txt.append(f"input{i}.txt")
        filenames_csv.append(f"input{i}.csv")
    ext.sort(filenames_txt, "txt_out.txt", type_data="i", bsize=10)
    ext.sort(filenames_csv, "csv_out.csv", type_data="i", key="b", bsize=10)


if __name__ == '__main__':
    # main()
    for_tests()