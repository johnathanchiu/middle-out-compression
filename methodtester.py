# test cases for employed algorithms
# © Johnathan Chiu, 2019

from middleout.MiddleOut import *
from middleout.runlength import rle, rld
from middleout.entropy_encoders import *

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
    def run_middleout(values, stride, encode):
        return MiddleOut.compress(values, stride, encode)

    @staticmethod
    def run_middelout_decomp(compressed_bytes):
        bits = unsigned_bin_list(compressed_bytes)
        return MiddleOut.decompress(bits)

    @staticmethod
    def test_middleout(bytes=None, stride=256, encoder=9, size=None, seeding=False, seed=1):
        if bytes is None:
            assert size is not None, "input a size for the dataset"
            bytes = TestMiddleOut.generate_random_data(size, seeding=seeding, seed=seed)
        print("size before middleout", len(bytes), "(bytes)", ", ", len(bytes) * 8, "(bits)")
        c = TestMiddleOut.run_middleout(bytes, stride, encoder)
        print("size of middleout", len(c), "bytes")
        de = TestMiddleOut.run_middelout_decomp(c)
        if len(bytes) < 1000: print("decompressed", de); print("original", bytes)
        TestMiddleOut.check_differences(bytes, de)
        print("compression: ", len(c) / len(bytes))

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
    TESTMO, TESTRL = False, False
    NUM_RUNS, LARGEST_GENERATED_NUM = 5, 255
    if TESTMO:
        for i in range(NUM_RUNS):
            size = np.random.randint(10000, 500000)
            seedstart = np.random.randint(1000000)
            print('size:', size); print('seed value:', seedstart)
            TestMiddleOut.test_middleout(stride=256, encoder=9, size=size, seeding=True, seed=seedstart)
    file_name = '/Users/johnathanchiu/Documents/jpeg-research/CompressionPics/tests/IMG_1072.jpg'
    bytes_of_file = read_file_bytes(file_name)
    TestMiddleOut.test_middleout(bytes=bytes_of_file, stride=256, encoder=9, size=443, seeding=True, seed=113924)
    if TESTRL:
        for i in range(NUM_RUNS):
            size = np.random.randint(10000, 10000000)
            seedstart = np.random.randint(1000000)
            print('size:', size); print('seed value:', seedstart)
            TestMiddleOut.test_runlength(size=size, seeding=True, seed=seedstart)
    print("\nfinished running all tests, all test cases passed!")
    print("--- %s seconds ---" % (time.time() - start_time))

