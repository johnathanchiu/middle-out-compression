from middleOut.MiddleOut import *
from middleOut.rle import rle, rld

import numpy as np

import random
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
        return np.random.randint(0, 255, size=size).tolist()

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
    def rletest(values):
        return rle(values)

    @staticmethod
    def rldtest(comp):
        return rld(comp)


if __name__ == '__main__':
    start_time = time.time()
    TestMiddleOut.test_middleout(size=10, libsize=2, seeding=False, debug=False)
    print("--- %s seconds ---" % (time.time() - start_time))

