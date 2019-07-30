# test cases for employed algorithms
# © Johnathan Chiu, 2019

from middleout.MiddleOut import *
from middleout.runlength import rle, rld

import numpy as np

import time


class TestMiddleOut:

    @staticmethod
    def check_differences(checker, sample, arr=True):
        def end_of_loop():
            return StopIteration
        size = len(checker); boolarr = []
        try:
            assert size == len(sample)
        except AssertionError:
            print("wrong lengths")
            print("expected length:", len(checker), ", returned length:", len(sample))
            exit(0)
        size = len(checker) if len(checker) < len(sample) else len(sample)
        [boolarr.append(True) if checker[count] == sample[count] else end_of_loop() for count in range(size)]
        try:
            assert len(boolarr) == size
        except AssertionError:
            err = len(boolarr)
            print("error in decompression at count " + str(err) + " (starts here): ",  sample[err:])
            exit(0)
        if arr: print("arrays are the same")
        else: print("bitsets are the same")

    @staticmethod
    def generate_random_data(size, seeding=False, seed=10):
        if seeding:
            np.random.seed(seed)
        return np.random.randint(0, LARGEST_GENERATED_NUM, size=size).tolist()

    @staticmethod
    def run_middleout(bytes, size=2, debug=False):
        return MiddleOut.middle_out(bytes, size=size)

    @staticmethod
    def run_middelout_decomp(bits, debug=False):
        return MiddleOut.middle_out_decomp(bits)

    @staticmethod
    def test_middleout(bytes=None, size=5, libsize=2, seeding=False, seed=1, debug=False):
        if bytes is None:
            bytes = TestMiddleOut.generate_random_data(size, seeding=seeding, seed=seed)
        print("size before middleout", len(bytes), "(bytes)", ", ", len(bytes) * 8, "(bits)")
        c = TestMiddleOut.run_middleout(bytes, size=libsize, debug=debug)
        if len(bytes) < 1000: print("size of middleout", len(c) // 8, "bytes")
        de = TestMiddleOut.run_middelout_decomp(c, debug=debug)
        if len(bytes) < 1000: print("decompressed", de); print("original", bytes)
        TestMiddleOut.check_differences(bytes, de)
        print("compression: ", (len(c) // 8) / len(bytes))

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
        rl = TestMiddleOut.rletest(arr, debug=debug)
        rd = TestMiddleOut.rldtest(rl, debug=debug)
        TestMiddleOut.check_differences(arr, rd)


if __name__ == '__main__':
    start_time = time.time()
    TESTMO = True
    TESTRL = False
    NUM_RUNS = 5
    LARGEST_GENERATED_NUM = 255
    if TESTMO:
        for i in range(NUM_RUNS):
            size = np.random.randint(10000, 1000000)
            seedstart = np.random.randint(1000000)
            print('size:', size)
            print('seed value:', seedstart)
            TestMiddleOut.test_middleout(size=size, libsize=2, seeding=True, seed=seedstart, debug=False)
    # TestMiddleOut.test_middleout([240, 240, 255, 240], size=0, libsize=2, seeding=True, seed=0, debug=False)
    if TESTRL:
        for i in range(NUM_RUNS):
            size = np.random.randint(10000, 10000000)
            seedstart = np.random.randint(1000000)
            print('size:', size)
            print('seed value:', seedstart)
            TestMiddleOut.test_runlength(size=size, seeding=True, seed=seedstart, debug=False)
    print("\nfinished running all tests, all test cases passed!")
    print("--- %s seconds ---" % (time.time() - start_time))

