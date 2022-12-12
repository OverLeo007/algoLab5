import io
import os

FILE_DIR = r"C:\Users\leva\PycharmProjects\algoLab5\files"


class IO:
    def __init__(self, filename, mode):
        self.mode = mode
        self.filename = filename
        self.file = open(os.path.join(FILE_DIR, filename), mode)

    def read(self):
        if self.mode != "r":
            raise io.UnsupportedOperation("not readable")
        res = []
        while True:
            char = self.file.read(1)
            if char == "":
                break
            if char == "\n":
                return int("".join(res))
            res.append(char)
        return False

    def change_mode(self, new_mode):
        self.mode = new_mode
        self.file.close()
        self.file = open(os.path.join(FILE_DIR, self.filename), self.mode)

    def write(self, num):
        if not isinstance(num, int):
            raise ValueError
        if self.mode != "w":
            raise io.UnsupportedOperation("not writable")
        self.file.write(f"{num}\n")

    def __del__(self):
        print("file", self.filename, "closed")
        self.file.close()


def generate_input(file_name="input.txt"):
    from random import shuffle
    with open(os.path.join(FILE_DIR, file_name), "w") as file:
        res = [i for i in range(1, 21)]
        shuffle(res)
        for i in res:
            file.write(f"{i}\n")


def sort(filename="input.txt"):
    inp = IO(filename, "r")
    f1 = IO("line1.txt", "w")
    f2 = IO("line2.txt", "w")

    f3 = IO("line3.txt", "w")
    # f4 = IO("line4.txt", "w")

    def split():
        inp.change_mode("r")
        f1.change_mode("w")
        f2.change_mode("w")

        is_low_line = True
        prev_num = inp.read()
        is_ended = False
        while True:
            if is_ended:
                break
            if is_low_line:
                cur_out_line = f1
            else:
                cur_out_line = f2

            # print(prev_num)
            cur_out_line.write(prev_num)

            while True:

                if not (next_num := inp.read()):
                    is_ended = True
                    break

                if next_num < prev_num:
                    is_low_line = not is_low_line
                    prev_num = next_num
                    break
                else:
                    prev_num = next_num
                    cur_out_line.write(next_num)

    def merge(out=inp):

        f1.change_mode("r")
        f2.change_mode("r")

        f1_next = f1.read()

        if not (f2_next := f2.read()):
            return True

        out.change_mode("w")

        f1_end = False
        f2_end = False
        f1_count = 0
        f2_count = 0

        while not (f1_end or f2_end):
            if f1_next < f2_next:
                out.write(f1_next)
                f1_count += 1

                if not (f1_next := f1.read()):
                    f1_end = True
            else:
                f2_count += 1
                out.write(f2_next)

                if not (f2_next := f2.read()):
                    f2_end = True

        if not f1_end:
            while True:
                if not (f1_next := f1.read()):
                    print()
                    break

                out.write(f1.read())
                f1_count += 1
                print("f1_add", f1_next)

        if not f2_end:
            while True:
                if not (f2_next := f2.read()):
                    print()
                    break

                out.write(f2.read())
                f2_count += 1
                print("f2_add", f2_next)
        print(f1_count, f2_count)

    # while True:
    #     split()
    #     if merge(f3):
    #         break
    split()
    # merge()
    # split()
    # merge()
    # split()
    # merge()
    # split()


def main():
    read_file = IO("input.txt", "r")
    print(read_file.read())
    print(read_file.read())


if __name__ == '__main__':
    generate_input()
    sort()
    # main()
