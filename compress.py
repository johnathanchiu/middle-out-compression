from middleout.MiddleOut import MiddleOut
from middleout.entropy_encoders import *
from middleout.utils import *

import os

import argparse
from tqdm import tqdm
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
    bytes_of_file = readFileBytes(file_name)
    partitions = split_file(bytes_of_file, chunksize=len(bytes_of_file))
    start_time = time.time()

    total_size = 0
    pbar = tqdm(partitions, desc='running middle-out compression scheme')
    for p in pbar:
        mo_compressed = MiddleOut.middle_out(lz4compressor(p))
        writeFileBytes(mo_compressed, fileName=compressed_file+'.bin')
        total_size += len(mo_compressed)

    print("compression converges!")
    compressed_size = total_size // 8
    print("size of resulting file:", compressed_size)
    print("compression percentage (compressed / original): ", compressed_size / size_of_file(file_name) * 100, "%")
    print("--- %s seconds ---" % (time.time() - start_time))
