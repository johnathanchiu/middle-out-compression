from middleOut.MiddleOut import *

import numpy as np

import random
import time


class TestMiddleOut:

    @staticmethod
    def check_differences(a, b, array=True):
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
        if array:
            print("arrays are the same")
        else:
            print("bitsets are the same")

    @staticmethod
    def generate_random_data(size, seeding=False, seed=10):
        if seeding:
            np.random.seed(seed)
        return np.random.randint(100, size=size)

    @staticmethod
    def run_middleout(bytes):
        return MiddleOut.middle_out(bytes, size=2, debug=False)

    @staticmethod
    def run_middelout_decomp(bits):
        return MiddleOut.middle_out_decompress(bits, debug=False)


if __name__ == '__main__':
    start_time = time.time()
    # test = [12, 11, 10, 9, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    # test = [1, 1, 1, 1, 2, 2, 2, 2, 0]
    # test = [255, 216, 255, 224, 0, 16, 74, 70, 73, 70]
    test = TestMiddleOut.generate_random_data(100, seeding=True, seed=8)
    # test[:] = [b-128 for b in test]
    print("size before middleout", len(test), "(bytes)", ", ", len(test) * 8, "(bits)")
    c = TestMiddleOut.run_middleout(test)
    print("size of middleout", len(c))
    de = TestMiddleOut.run_middelout_decomp(c)
    print("decompressed", de, "original", test)
    TestMiddleOut.check_differences(test, de)
    print("--- %s seconds ---" % (time.time() - start_time))

