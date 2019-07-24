from middleout.MiddleOut import *
from middleout.rle import rle, rld

import numpy as np

import time


class TestMiddleOut:

    @staticmethod
    def check_differences(checker, sample, arr=True):
        def end_of_loop():
            return StopIteration
        size = len(checker); boolarr = []
        if len(checker) != len(sample):
            print("wrong lengths")
            size = len(checker) if len(checker) < len(sample) else len(sample)
        [boolarr.append(True) if checker[count] == sample[count] else end_of_loop() for count in range(size)]
        if len(boolarr) == size:
            if arr: print("arrays are the same")
            else: print("bitsets are the same")
            return
        err = len(boolarr)
        print("error in decompression at count " + str(err) + " (starts here): ",  sample[err:])

    @staticmethod
    def generate_random_data(size, seeding=False, seed=10):
        if seeding:
            np.random.seed(seed)
        return np.random.randint(0, 5, size=size).tolist()

    @staticmethod
    def run_middleout(bytes, size=2, debug=False):
        return MiddleOut.middle_out(bytes, size=size, debug=debug)

    @staticmethod
    def run_middelout_decomp(bits, debug=False):
        return MiddleOut.middle_out_decompress(bits, debug=debug)

    @staticmethod
    def test_middleout(bytes=None, size=5, libsize=2, seeding=False, seed=1, debug=False):
        if bytes is None:
            bytes = TestMiddleOut.generate_random_data(size, seeding=seeding, seed=seed)
        print("size before middleout", len(bytes), "(bytes)", ", ", len(bytes) * 8, "(bits)")
        c = TestMiddleOut.run_middleout(bytes, size=libsize, debug=debug)
        print("size of middleout", len(c))
        de = TestMiddleOut.run_middelout_decomp(c, debug=debug)
        print("decompressed", de); print("original", bytes)
        TestMiddleOut.check_differences(bytes, de)
        print("compression: ", len(c) / (len(bytes) * 8))

    @staticmethod
    def rletest(values, debug=False):
        return rle(values, debug=debug)

    @staticmethod
    def rldtest(comp, debug=False):
        return rld(comp, debug=debug)

    @staticmethod
    def test_runlength(arr=None, size=100, seeding=False, seed=1, debug=False):
        if arr is None:
            arr = TestMiddleOut.generate_random_data(size, seeding=seeding, seed=seed)
        print("original values: ", arr)
        rl = TestMiddleOut.rletest(arr, debug=debug)
        print("result of run length: ", rl)
        rd = TestMiddleOut.rldtest(rl, debug=debug)
        print("result of decode: ", rd)
        TestMiddleOut.check_differences(arr, rd)


if __name__ == '__main__':
    start_time = time.time()
    TestMiddleOut.test_middleout(size=5, libsize=3, seeding=False, debug=False)
    TestMiddleOut.test_runlength(size=3000000, seeding=False, seed=1, debug=False)
    print("--- %s seconds ---" % (time.time() - start_time))

