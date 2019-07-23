from middleout.utils import readFileBytes, writeFile, size_of_file, pad_stream, convertBin, split_file
from middleout.MiddleOut import MiddleOut

import array
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
    bytes_of_file = array.array('b', [b - 128 for b in bytes_of_file])
    partitions = split_file(bytes_of_file, chunksize=len(bytes_of_file))
    start_time = time.time()

    total_size = 0
    pbar = tqdm(partitions)
    for p in pbar:
        pbar.set_description("running middle-out compression scheme")
        mo_compressed = MiddleOut.middle_out(p, size=3)
        pad = pad_stream(len(mo_compressed))
        num_padded = convertBin(pad, bits=4)
        mo_compressed += ('0' * pad) + num_padded
        writeFile(mo_compressed, fileName=compressed_file)
        total_size += len(mo_compressed)

    print("compression converges!")
    compressed_size = total_size // 8
    print("size of resulting file:", compressed_size)
    print("compression percentage (compressed / original): ", compressed_size / size_of_file(file_name) * 100, "%")
    print("--- %s seconds ---" % (time.time() - start_time))
