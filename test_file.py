from middleout.MiddleOut import *
from middleout.entropy_encoders import *

import time


file_name = '/Users/johnathanchiu/Documents/jpeg-research/CompressionPics/tests/IMG_1072.jpg'
bytes_of_file = lz4compressor(readFileBytes(file_name))


def main():
    comp = MiddleOut.middle_out(bytes_of_file)
    decomp = MiddleOut.middle_out_decomp(comp)
    print(len(decomp) // 8 / len(bytes_of_file))


if __name__ == '__main__':
    main()
    start = time.time()
    print("--- %s seconds ---" % (time.time() - start))
