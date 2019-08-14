from middleout.middle_out import MiddleOut
from middleout.entropy_encoders import *
from middleout.huffman import *
from middleout.utils import *

import os

import argparse
import time

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('-o', "--original", required=True, help="Path to file")
    ap.add_argument("-c", "--compressed", required=False, default="./",
                    help="Dir. to save file to")
    args = ap.parse_args()
    file_name = args.original
    compressed_file = args.compressed + os.path.splitext(os.path.basename(file_name))[0] + \
                      os.path.splitext(os.path.basename(file_name))[1]
    bytes_of_file = read_file_bytes(file_name)
    start_time = time.time()

    frame = Huffman()
    compressed = MiddleOut.compress(lz4compressor(bytes_of_file), stride=512)
    compressed = frame.compress(compressed)

    write_file_bytes(compressed, fileName=compressed_file + '.bin')

    print("compression converges!")
    print("size of resulting file:", len(compressed))
    print("compression percentage (compressed / original): ", len(compressed) / size_of_file(file_name) * 100, "%")
    print("--- %s seconds ---" % (time.time() - start_time))
