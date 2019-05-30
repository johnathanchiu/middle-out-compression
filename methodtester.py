from middleOut.MiddleOut import *
from middleOut.EntropyReduction import *

import unittest

import random
import time


class TestMiddleOut:

    @staticmethod
    def check_differences(a, b):
        counter = len(a)
        if len(a) != len(b):
            print("wrong lengths")
            counter = len(a) if len(a) > len(b) else len(b)
        count = 0
        while count < counter:
            if a[count] != b[count]:
                print("error starts here: ", b[count:])
                return
            count += 1
        print("bitsets are the same")

    @staticmethod
    def generate_random_bitset(bitset_size, set_seed=False, seed=0):
        x, y = [], []
        if (set_seed):
            random.seed(seed)
        for _ in range(bitset_size):
            tem = random.randint(0, 50)
            x.append(tem)
            y.append(tem)
        return MiddleOutUtils.convertBin_list(x), y

    @staticmethod
    def test_random_mo(bitset_size, set_seed=False, seed=0):
        x = []
        if (set_seed):
            random.seed(seed)
        for _ in range(bitset_size):
            tem = random.randint(0, 30)
            x.append(tem)
        return MiddleOut.middle_out(x)

    @staticmethod
    def run_middleout(bytes):
        return MiddleOut.middle_out(bytes, b=16)

if __name__ == '__main__':
    start_time = time.time()
    # _, test_list = TestMiddleOut.generate_random_bitset(1000, set_seed=True, seed=8)
    # EntropyReduction.bz2(test_list, '/Users/johnathanchiu/Downloads/test')
    # compressed = TestMiddleOut.test_middleout_compression(1000, set_seed=True, seed=8)
    # uncompressed = TestMiddleOut.test_middleout_decompression(compressed)
    # TestMiddleOut.check_differences(test_list, uncompressed)
    l = [-28, -6, -4, -1, -2, -2, 0, 1, 0, 1, 0, -29, 0, -2, -1, 0, -1, 0, 1, 0, -27, 0, 3, -1, 0, 1, 0, 0, 0, 0, -4, 3, -1, -1, 1, 0, -1, 0]
    c = TestMiddleOut.run_middleout(l)
    # print("len of compressed", len(compressed))
    print("--- %s seconds ---" % (time.time() - start_time))

