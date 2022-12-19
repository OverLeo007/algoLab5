from functools import wraps
from io import UnsupportedOperation
import os
from random import randint
from time import time
from typing import Optional, Callable, Union, Iterable

from internal_sort import merge_sort

TEMP_DIR = r"temp"
EOF = "¶"


def is_sorted(filename: str) -> bool:
    """
    Функция проверки txt файла на отсортированность по неубвыванию
    :param filename: имя файла
    :return: bool результат проверки
    """
    with open(filename) as file:
        res = list(map(lambda x: int(x.replace("\n", "")), file.readlines()))
        return res == sorted(res)


def timing(f: Callable):
    """
    Декоратор для вычисления времени выполнения сортировки
    @param f: функция, время которой засекаем
    """

    @wraps(f)
    def wrap(*args, **kw):
        ts = time()
        result = f(*args, **kw)
        te = time()
        print(
            f'func: {f.__name__}'
            f'time: {te - ts:2.4f} sec')
        return result

    return wrap


class IO:
    def __init__(self, filename, mode, data_type="s", is_temp=False):
        self.mode = mode
        self.filename = filename
        self.is_temp = is_temp
        self.descr = {"i": int, "s": str, "f": float}[data_type]

        try:
            os.mkdir(TEMP_DIR)
        except FileExistsError:
            pass
        self.path = os.path.join(TEMP_DIR, filename) if is_temp else filename
        self.file = open(self.path, mode)

    def read(self):
        if self.mode != "r":
            raise UnsupportedOperation("not readable")
        res = []
        while True:
            char = self.file.read(1)
            if char == "":
                break
            if char == "\n":
                if (val := "".join(res)) != "None":

                    return self.descr(val)
                else:
                    return EOF
            res.append(char)

        return EOF

    def is_empty(self):
        self.file.seek(0, 0)
        data = self.file.read()
        self.file.seek(0, 0)
        if not data:
            return True
        return False

    def read_buffer(self, buffer_size):
        res = []
        for i in range(buffer_size):
            if (num := self.read()) != EOF:
                res.append(num)
            else:
                break
        return res

    def get_buffer(self, buffer_size):
        res = []
        for i in range(buffer_size):
            num = self.read()
            if num is False:
                return res
            res.append(num)
        return res

    def change_mode(self, new_mode):
        self.mode = new_mode
        self.file.close()
        self.file = open(self.path, self.mode)

    def write(self, num):
        # if not isinstance(num, int):
        #     raise ValueError
        if self.mode != "w":
            raise UnsupportedOperation("not writable")
        self.file.write(f"{num}\n")

    def copy_to(self, out_file):
        out_file: IO
        out_file.change_mode("w")
        self.change_mode("r")
        while (char := self.file.read()) != "":
            out_file.file.write(char)

    def write_buffer(self, buffer):
        for el in buffer:
            self.write(el)

    def __repr__(self):
        return f"'{self.filename}'(mode: {self.mode}, is_temp: {self.is_temp})"

    def __del__(self):
        # print("file", self.filename, "closed")
        self.file.close()
        if self.is_temp:
            os.remove(self.path)
        try:
            if not os.listdir(TEMP_DIR):
                os.rmdir(TEMP_DIR)
        except FileNotFoundError:
            pass


def generate_input(file_name="input.txt"):
    """
    Функция генерации случайно заполненного txt файла
    :param file_name:
    """
    from random import shuffle
    with open(file_name, "w") as file:
        res = [randint(-100, 1000) for _ in range(1, 201)]
        shuffle(res)
        for i in res:
            file.write(f"{i}\n")


@timing
def my_sort(src: Union[Iterable, str] = "input.txt",
            output: Optional[str] = None,
            reverse: bool = False,
            type_data: Optional[str] = None,
            key: Optional[str] = None,
            bsize=1000) -> None:
    """
    Функция сортировки, реализующая алгоритм сбалансированного двухпутевого слияния
    :param src: файл(ы) с исходными данными
    :param output: выходной файл
    :param reverse: флаг сортировки по невозрастанию
    :param type_data: тип передаваемых значений
    :param key: ключ для csv файла
    :param bsize: размер буфера для внутренней сортировки
    """
    if output == "":
        output = None

    input_files = []
    if not isinstance(src, str):
        for file in src:
            input_files.append(IO(file, "r", type_data))
    else:
        input_files.append(IO(src, "r", type_data))

    def external_sort(inp: IO, file_num: int = 1) -> IO:
        """
        Функция внешней сортировки
        :param inp: Открытый файл, обернутый в IO с исходным набором данных
        :param file_num: номер файла
        :return: файл, обернутый в IO, в котором хранятся отсортированные значения
        """
        if inp.is_empty():
            return inp
        tape1 = IO(f"line1_{file_num}.txt", "w", type_data, is_temp=True)
        tape2 = IO(f"line2_{file_num}.txt", "w", type_data, is_temp=True)
        tape3 = IO(f"line3_{file_num}.txt", "w", type_data, is_temp=True)
        tape4 = IO(f"line4_{file_num}.txt", "w", type_data, is_temp=True)
        pass_num = 1

        def split():
            """
            Функция предварительного разбиения исходного файла на два,
            сортируя блоки по bsize элементов
            """
            is_tape1 = True

            while True:
                buf = inp.read_buffer(bsize)
                merge_sort(buf, reverse)
                if is_tape1:
                    tape1.write_buffer(buf)
                else:
                    tape2.write_buffer(buf)

                is_tape1 = not is_tape1

                if len(buf) != bsize:
                    break

        def merge():
            """
            Функция слияния последовательностей из файлов
            :return: False, если требуется еще merge(),
            файл, в котором хранятся отсортированные данные в противном случае
            """
            if pass_num % 2 != 0:
                tape1.change_mode("r")
                tape2.change_mode("r")
                tape3.change_mode("w")
                tape4.change_mode("w")
                read1, read2 = tape1, tape2
                write1, write2 = tape3, tape4
            else:
                tape1.change_mode("w")
                tape2.change_mode("w")
                tape3.change_mode("r")
                tape4.change_mode("r")
                read1, read2 = tape3, tape4
                write1, write2 = tape1, tape2

            # print(write1.filename, write2.filename, read1.filename, read2.filename)

            is_write1 = True
            writes_count = 0
            while True:

                write_file = write1 if is_write1 else write2
                # print(f"Сливаем в {write_file.filename}")

                seq1_len = 2 ** (pass_num - 1) * bsize
                seq2_len = 2 ** (pass_num - 1) * bsize

                i = j = 0

                is_seq1_read, is_seq2_read = True, True
                seq1_elem = seq2_elem = None

                while i < seq1_len and j < seq2_len:

                    if seq1_elem == EOF or seq2_elem == EOF:
                        # print(seq1_elem, seq2_elem, "212 EOF ALL")
                        break

                    if is_seq1_read:
                        seq1_elem = read1.read()
                    if seq1_elem == EOF:
                        # print(seq1_elem, "218 EOF 1")
                        break
                    if is_seq2_read:
                        seq2_elem = read2.read()

                    if seq2_elem == EOF:
                        # print(seq2_elem, "224 EOF 2")
                        break

                    # if reverse != key(seq1_elem) < key(seq2_elem):
                    if seq1_elem > seq2_elem if reverse \
                            else seq1_elem < seq2_elem:
                        write_file.write(seq1_elem)
                        i += 1
                        is_seq1_read, is_seq2_read = True, False

                    else:
                        write_file.write(seq2_elem)
                        j += 1
                        is_seq1_read, is_seq2_read = False, True

                fix_i, fix_j = i, j
                for i in range(seq1_len - fix_i):

                    if seq1_elem == EOF:
                        # print(seq1_elem, "241 EOF 1")
                        break
                    write_file.write(seq1_elem)
                    if i != seq1_len - fix_i - 1:
                        seq1_elem = read1.read()

                for j in range(seq2_len - fix_j):
                    if seq2_elem == EOF:
                        # print(seq2_elem, "249 EOF 2")
                        break
                    write_file.write(seq2_elem)
                    if j != seq2_len - fix_j - 1:
                        seq2_elem = read2.read()

                is_write1 = not is_write1
                if seq1_elem == EOF or seq2_elem == EOF:
                    # print(seq1_elem, seq2_elem, "258 EOF ALL")
                    break

                writes_count += 1
            if read1.is_empty() is not read2.is_empty():
                if not read1.is_empty():
                    return read1
                return read2
            return False

        split()
        while True:
            result_file = merge()
            if result_file:
                break
            pass_num += 1
        return result_file

    res_files = []
    for n, file in enumerate(input_files):
        res_files.append(external_sort(file, n))

    if output is None:
        for n, file in enumerate(res_files):
            out = input_files[n]
            file.copy_to(out)
    else:
        out = IO(output, "w")
        merge_to_one(res_files, out, reverse)


def merge_to_one(src: list[IO, ...], out: IO, reverse=False) -> None:
    """
    Функция слияния отсортированных файлов в один
    :param src: исходные файлы
    :param out: выходной файл
    :param reverse: флаг сортировки по невозрастанию
    """
    is_read_dict = {i: {"value": file.read(), "is_read": False}
                    for i, file in enumerate(src)}

    def find_val():
        func = max if reverse else min
        return func(is_read_dict.items(), key=lambda x: x[1]["value"])

    def dict_upd():
        to_del = []
        for k, v in is_read_dict.items():
            if v["is_read"] is True:
                v["value"] = src[k].read()
                v["is_read"] = False

            if v["value"] == EOF:
                to_del.append(k)
        for k in to_del:
            del is_read_dict[k]

    while is_read_dict:
        need_val = find_val()
        out.write(need_val[1]["value"])
        is_read_dict[need_val[0]]["is_read"] = True
        dict_upd()


def main():
    src = [IO(filename, "r", data_type="i") for filename in
           filter(lambda x: x.startswith("input"), os.listdir())]
    out = IO("output.txt", "w")
    merge_to_one(src, out)


if __name__ == '__main__':
    filenames = []
    for ind in range(10):
        new_name = f"input{ind}.txt"
        filenames.append(new_name)
        generate_input(new_name)
    my_sort(filenames, output="output.txt", type_data="i", bsize=10)
    for name in filenames:
        print(name, is_sorted(name))
    # generate_input()
    # my_sort("27989_B.txt", type_data="i", bsize=1000)
    # main()
