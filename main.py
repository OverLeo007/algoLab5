from io import UnsupportedOperation
import os

from internal_sort import merge_sort

FILE_DIR = r"C:\Users\sokol\PycharmProjects\algoLab5\files"


class IO:
    def __init__(self, filename, mode):
        self.mode = mode
        self.filename = filename
        self.file = open(os.path.join(FILE_DIR, filename), mode)

    def read(self):
        if self.mode != "r":
            raise UnsupportedOperation("not readable")
        res = []
        while True:
            char = self.file.read(1)
            if char == "":
                break
            if char == "\n":
                return int("".join(res))
            res.append(char)
        return False

    def read_buffer(self, buffer_size):
        res = []
        for i in range(buffer_size):
            if num := self.read():
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
        self.file = open(os.path.join(FILE_DIR, self.filename), self.mode)

    def write(self, num):
        # if not isinstance(num, int):
        #     raise ValueError
        if self.mode != "w":
            raise UnsupportedOperation("not writable")
        self.file.write(f"{num}\n")

    def write_buffer(self, buffer):
        for el in buffer:
            self.write(el)

    def __del__(self):
        print("file", self.filename, "closed")
        self.file.close()


def generate_input(file_name="input.txt"):
    from random import shuffle
    with open(os.path.join(FILE_DIR, file_name), "w") as file:
        res = [i for i in range(1, 100)]
        shuffle(res)
        for i in res:
            file.write(f"{i}\n")


def sort(buffer_size=1000, filename="input.txt"):
    inp = IO(filename, "r")
    tape1 = IO("line1.txt", "w")
    tape2 = IO("line2.txt", "w")

    tape3 = IO("line3.txt", "w")
    tape4 = IO("line4.txt", "w")

    def split():

        is_tape1 = True

        while True:
            buf = inp.read_buffer(buffer_size)
            merge_sort(buf)
            if is_tape1:
                tape1.write_buffer(buf)
            else:
                tape2.write_buffer(buf)

            is_tape1 = not is_tape1

            if len(buf) != buffer_size:
                break

    def merge(from_tape_num):
        if from_tape_num == 1:
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
        last_seq = False

        while True:

            if last_seq:
                break

            seq1 = read1.read_buffer(buffer_size)
            seq2 = read2.read_buffer(buffer_size)
            print(seq1, seq2, sep="\n")
            i = 0
            j = 0
            while i < len(seq1) and j < len(seq2):
                if seq1[i] < seq2[j]:
                    if is_write1:
                        write1.write(seq1[i])
                    else:
                        write2.write(seq1[i])
                    i += 1
                else:
                    if is_write1:
                        write1.write(seq2[j])
                    else:
                        write2.write(seq2[j])
                    j += 1

            while i < len(seq1):
                if is_write1:
                    write1.write(seq1[i])
                else:
                    write2.write(seq1[i])
                i += 1

            while j < len(seq2):
                if is_write1:
                    write1.write(seq2[j])
                else:
                    write2.write(seq2[j])
                j += 1

            is_write1 = not is_write1
            if len(seq1) != len(seq2):
                last_seq = True

    split()
    merge(1)


def main():
    read_file = IO("input.txt", "r")
    print(read_file.read())
    print(read_file.read())


if __name__ == '__main__':
    # generate_input()
    sort(buffer_size=10)
    # main()
