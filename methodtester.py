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
    def test_middleout(bitset_size, set_seed=False, seed=0):
        x = []
        bztest = []
        if (set_seed):
            random.seed(seed)
        for _ in range(bitset_size):
            tem = random.randint(0, 30)
            x.append(tem)
            bztest.append(tem)

        x = MiddleOutUtils.convertBin_list(x)
        EntropyReduction.bz2(bztest, '/Users/johnathanchiu/Downloads/test')
        comp = MiddleOut.middle_out(x)
        z = MiddleOut.decompressStream(comp)
        print("compressed bits: ", bitset_size - len(comp))
        return x, z


if __name__ == '__main__':
    start_time = time.time()
    bitseta, bitsetb = TestMiddleOut.test_middleout(100000, set_seed=True, seed=10)
    TestMiddleOut.check_differences(bitseta, bitsetb)
    print("--- %s seconds ---" % (time.time() - start_time))

