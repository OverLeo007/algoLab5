import csv
from functools import wraps
from io import UnsupportedOperation
import os
from time import time
from typing import Optional, Callable, Union, Iterable

from internal_sort import merge_sort

TEMP_DIR = r"temp"
EOF = "¶"
CsvRow = dict[str, Union[int, float, str]]


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
            f'func: {f.__name__} '
            f'time: {te - ts:2.4f} sec')
        return result

    return wrap


class IO:
    """
    Класс реализации ввода-вывода для txt и csv файлов
    """
    def __init__(self, filename: str, mode: str, data_type: str = "s",
                 is_temp: bool = False,
                 delimiter: str = ",",
                 header: Optional[list[str, ...]] = None,
                 key_val: Optional[str] = None):
        """
        Инициализация экземпляра класса
        :param filename: имя файла
        :param mode: режим открытия файла (r, w)
        :param data_type: тип данных, столбца сортировки
        или значения на каждой строке
        :param is_temp: флаг временного файла
        :param delimiter: разделитель для csv
        :param header: заголовок для csv файлов, открытых в режиме "w"
        :param key_val: ключевое значение, по которому производится сортировка
        """
        self.mode = mode
        self.filename = filename
        self.is_temp = is_temp
        self.descr = {"i": int, "s": str, "f": float}[data_type]
        self.header = header

        try:
            os.mkdir(TEMP_DIR)
        except FileExistsError:
            pass

        self.path = os.path.join(TEMP_DIR, filename) if is_temp else filename

        self.is_txt = self.path.endswith(".txt")
        self.file = open(self.path, mode, newline="") if not self.is_txt \
            else open(self.path, mode)
        self.key = key_val
        if not self.is_txt:
            self.delimiter = delimiter
            if mode == "r":
                self.csv_access = csv.DictReader(self.file,
                                                 delimiter=delimiter)
                self.header = self.csv_access.fieldnames

            else:
                self.csv_access = csv.DictWriter(self.file, header,
                                                 delimiter=delimiter)
                self.csv_access.writeheader()
            self.key = self.key if self.key else self.header[0]
            if header is None and mode == "w":
                raise TypeError("mode is write and header is not given")

    def _read_txt(self) -> Union[int, float, str]:
        """
        Метод считывания одной строки из txt файла
        :return: строка, приведенная к data_type типу
        """
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

    def _read_csv(self) -> Union[str, CsvRow]:
        """
        Метод считывания одной строки из csv файла
        :return: словарь, где ключи - заголовки текущего столбца
        """
        if self.mode != "r":
            raise UnsupportedOperation("not readable")
        try:
            res = next(self.csv_access)  # noqa
            res[self.key] = self.descr(res[self.key])
        except StopIteration:
            return EOF
        return res

    def read(self) -> Union[str, int, float, CsvRow]:
        """
        Универсальный метод чтения для любых файлов
        :return: считанное значение
        """
        if self.is_txt:
            return self._read_txt()
        else:
            return self._read_csv()

    def _is_txt_empty(self) -> bool:
        """
        Проверка txt файла на пустоту
        :return: True если файл пустой, False в противном случае
        """
        self.file.seek(0, 0)
        data = self.file.read()
        self.file.seek(0, 0)
        if not data:
            return True
        return False

    def _is_csv_empty(self) -> bool:
        """
        Проверка txt файла на пустоту
        :return: True если файл пустой, False в противном случае
        """
        try:
            self.file.seek(0, 0)
            next(self.csv_access)  # noqa
            next(self.csv_access)  # noqa
            self.file.seek(0, 0)
            next(self.csv_access)  # noqa

        except StopIteration:
            return True
        return False

    def is_empty(self) -> bool:
        """
        Универсальный метод проверки на пустот для txt и csv
        :return: True если файл пустой, False в противном случае
        """
        if self.is_txt:
            return self._is_txt_empty()
        else:
            return self._is_csv_empty()

    def read_buffer(self, buffer_size: int)\
            -> list[Union[str, int, float, CsvRow], ...]:
        """
        Метод считывания данных, в определённом кол-ве
        :param buffer_size: сколько строк файла нужно считать
        :return: список со строками файла
        """
        res = []
        for i in range(buffer_size):
            num = self.read()
            if num != EOF:
                res.append(num)
            else:
                break
        return res

    def change_mode(self, new_mode: str) -> None:
        """
        Метод смены режима файла с чтения на запись и обратно
        :param new_mode: новый режим
        """
        self.mode = new_mode
        self.file.close()

        if not self.is_txt:
            self.file = open(self.path, self.mode, newline="")
            if new_mode == "r":
                self.csv_access = csv.DictReader(self.file,
                                                 delimiter=self.delimiter)
            else:
                self.csv_access = csv.DictWriter(self.file, self.header,
                                                 delimiter=self.delimiter)
                self.csv_access.writeheader()
        else:
            self.file = open(self.path, self.mode)

    def _write_txt(self, val: Union[str, int, float]) -> None:
        """
        Метод для записи значения в txt файл
        :param val: значение
        """
        self.file.write(f"{val}\n")

    def _write_csv(self, row: CsvRow) -> None:
        """
        Метод для записи значения в csv файл
        :param row: значение
        """
        self.csv_access.writerow(row)

    def write(self, val: Union[str, int, float, CsvRow]) -> None:
        """
        Метод записи значения в файл
        :param val: значение
        """
        if self.mode != "w":
            raise UnsupportedOperation("not writable")
        if self.is_txt:
            self._write_txt(val)
        else:
            self._write_csv(val)

    def _txt_copy_to(self, out_file) -> None:
        """
        Метод копирования текущего txt файла в другой
        :param out_file: файл, в который копируем
        """
        while (char := self.file.read()) != "":
            out_file.file.write(char)

    def _csv_copy_to(self, out_file) -> None:
        """
        Метод копирования текущего csv файла в другой
        :param out_file: файл, в который копируем
        """
        while (res := self.read()) != EOF:
            out_file.write(res)

    def copy_to(self, out_file) -> None:
        """
        Метод копирования текущего файла в другой
        :param out_file: файл, в который копируем
        """
        out_file.change_mode("w")
        self.change_mode("r")
        if self.is_txt:
            self._txt_copy_to(out_file)
        else:
            self._csv_copy_to(out_file)

    def write_buffer(self,
                     buffer: list[Union[int, float, str, CsvRow], ...]) -> None:
        """
        Метод записи списка значений в файл
        :param buffer: список значений
        """
        for el in buffer:
            self.write(el)

    def __repr__(self) -> str:
        return f"'{self.filename}'(mode: {self.mode}, is_temp: {self.is_temp})"

    def __del__(self) -> None:
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
    Генерация случайного входного txt файла
    :param file_name: имя файла
    """
    from random import shuffle, randint
    with open(file_name, "w") as file:
        res = [randint(-100, 1000) for _ in range(1, 201)]
        shuffle(res)
        for i in res:
            file.write(f"{i}\n")


def generate_csv_input(file_name="input.csv", delimiter=","):
    """
    Генерация случайного входного csv файла
    :param file_name: имя файла
    :param delimiter: разделитель между столбцами
    """
    from random import randint
    rows = list("abcd")
    with open(file_name, "w", newline="") as file:
        writer = csv.DictWriter(file, rows, delimiter=delimiter)
        writer.writeheader()
        for _ in range(200):
            writer.writerow({row: randint(-100, 1000) for row in rows})


# @timing
def my_sort(src: Union[Iterable, str] = "input.txt",
            output: Optional[str] = None,
            reverse: bool = False,
            type_data: Optional[str] = None,
            key: Optional[str] = None,
            delimiter: str = ",",
            bsize=1000) -> None:
    """
    Функция сортировки, реализующая алгоритм
    сбалансированной двухпутевой сортировки слиянием
    :param src: исходный файл(ы)
    :param output: выходной файл
    :param reverse: флаг сортировки по невозрастанию
    :param type_data: тип считываемых данных
    :param key: имя столбца по которому производим сортировку для csv
    :param delimiter: разделитель между столбцами для csv
    :param bsize: размер буфера, для внутренней сортировки
    """
    if output == "":
        output = None

    input_files = []
    if not isinstance(src, str):
        for file in src:
            input_files.append(IO(file, "r", type_data, delimiter=delimiter))
    else:
        input_files.append(IO(src, "r", type_data, delimiter=delimiter))

    header = None
    if not input_files[0].is_txt:
        header = input_files[0].header
        if key is None:
            key = header[0]
    file_ext = "txt" if input_files[0].is_txt else "csv"

    def external_sort(inp: IO, file_num: int = 1):
        """
        Функция внешней сортировки одного файла
        :param inp: входной файл
        :param file_num: номер входного файла
        :return: файл, в котором хранятся отсортированные значения
        """
        if inp.is_empty():
            return inp

        is_txt = inp.is_txt
        tape1 = IO(f"line1_{file_num}.{file_ext}", "w", type_data,
                   is_temp=True, header=header, key_val=key, delimiter=delimiter)
        tape2 = IO(f"line2_{file_num}.{file_ext}", "w", type_data,
                   is_temp=True, header=header, key_val=key, delimiter=delimiter)
        tape3 = IO(f"line3_{file_num}.{file_ext}", "w", type_data,
                   is_temp=True, header=header, key_val=key, delimiter=delimiter)
        tape4 = IO(f"line4_{file_num}.{file_ext}", "w", type_data,
                   is_temp=True, header=header, key_val=key, delimiter=delimiter)
        pass_num = 1

        def cmp(val1, val2):
            if is_txt:
                return val1 > val2 if reverse else val1 < val2
            return val1[key] > val2[key] if reverse else val1[key] < val2[key]

        def split():
            """
            Функция предварительного разделения содержимого
            исходной ленты на две другие ленты, сортирующая серии длины bsize
            """
            is_tape1 = True

            while True:
                buf = inp.read_buffer(bsize)
                merge_sort(buf, cmp=cmp)
                if is_tape1:
                    tape1.write_buffer(buf)
                else:
                    tape2.write_buffer(buf)

                is_tape1 = not is_tape1

                if len(buf) != bsize:
                    break

        def merge() -> Union[bool, IO]:
            """
            Функция слияния из двух лент, в другие две поочередно
            :return: False, если сортировка не закончена,
            файл, с отсортированным значениями в противном случае
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

            is_write1 = True
            writes_count = 0
            while True:

                write_file = write1 if is_write1 else write2

                seq1_len = 2 ** (pass_num - 1) * bsize
                seq2_len = 2 ** (pass_num - 1) * bsize

                i = j = 0

                is_seq1_read, is_seq2_read = True, True
                seq1_elem = seq2_elem = None

                while i < seq1_len and j < seq2_len:

                    if seq1_elem == EOF or seq2_elem == EOF:
                        break

                    if is_seq1_read:
                        seq1_elem = read1.read()
                    if seq1_elem == EOF:
                        break

                    if is_seq2_read:
                        seq2_elem = read2.read()
                    if seq2_elem == EOF:
                        break

                    if cmp(seq1_elem, seq2_elem):
                        write_file.write(seq1_elem)
                        i += 1
                        is_seq1_read, is_seq2_read = True, False

                    else:
                        write_file.write(seq2_elem)
                        j += 1
                        is_seq1_read, is_seq2_read = False, True

                fix_i, fix_j = i, j
                for i in range(seq1_len - fix_i):
                    if seq1_elem == EOF or seq1_elem is None:
                        # print(seq1_elem, "241 EOF 1")
                        break

                    write_file.write(seq1_elem)
                    if i != seq1_len - fix_i - 1:
                        seq1_elem = read1.read()

                for j in range(seq2_len - fix_j):
                    if seq2_elem == EOF or seq2_elem is None:
                        break
                    write_file.write(seq2_elem)
                    if j != seq2_len - fix_j - 1:
                        seq2_elem = read2.read()

                is_write1 = not is_write1
                if seq1_elem == EOF or seq2_elem == EOF:
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
        out = IO(output, "w", header=header, delimiter=delimiter)
        merge_to_one(res_files, out, reverse)


def merge_to_one(src: list[IO, ...], out: IO, reverse=False) -> None:
    """
    Функция слияния всех файлов в один
    :param src: исходные файлы
    :param out: выходной файл
    :param reverse: флаг сортировки по невозразстанию
    """
    is_read_dict = {i: {"value": file.read(), "is_read": False}
                    for i, file in enumerate(src)}

    def find_val():
        """
        Функция поиска минимального или максимального значения
        среди словаря элементов каждого файла
        :return: подходящий эелмент
        """
        func = max if reverse else min
        if src[0].is_txt:
            return func(is_read_dict.items(),
                        key=lambda x: x[1]["value"])
        else:
            return func(is_read_dict.items(),
                        key=lambda x: x[1]["value"][src[0].key])

    def dict_upd():
        """
        Функция обновления словаря текущих значений
        """
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
    filenames = []
    for ind in range(1, 5):
        name = f"inp{ind}.csv"
        generate_csv_input(name)
        filenames.append(name)
    my_sort(filenames, output="ult_out.csv", type_data="i",
            bsize=10, key="a", delimiter=",")


if __name__ == '__main__':
    main()
