from middleOut.MiddleOut import *

import unittest

import random
import time


class TestMiddleOut(unittest.TestCase):

    def check_differences(self, a, b):
        try:
            self.assertEqual(a, b)
        except:
            counter = len(a)
            if len(a) != len(b):
                print("wrong lengths")
                counter = len(a) if len(a) > len(b) else len(b)
            count = 0
            while count < counter:
                if a[count] != b[count]:
                    print("error starts here: ", a[count:])
                    return
                count += 1
        print("bitsets are the same")


    @staticmethod
    def test_middleout(bitset_size, set_seed=False, seed=0):
        x = ''
        if (set_seed):
            random.seed(seed)
        for _ in range(bitset_size):
            x += str(random.randint(0, 1))

        layer_one, uncomp_part = MiddleOut.zero_one_filter(x)
        lib = MiddleOut.build_library(uncomp_part)
        layer_two = MiddleOut.eight_bit_compression(uncomp_part, lib)
        y = MiddleOut.merge_compression(layer_one, layer_two)
        lib += y
        z = MiddleOut.decompressStream(lib)
        print("compressed bits: ", bitset_size - len(lib))
        return x, z


if __name__ == '__main__':
    start_time = time.time()
    for _ in range(100):
        bitseta, bisetb = TestMiddleOut.test_middleout(100000, set_seed=True)
        TestMiddleOut.check_differences(TestMiddleOut(), bitseta, bisetb)
    print("--- %s seconds ---" % (time.time() - start_time))

