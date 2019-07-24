from middleout.utils import *
from middleout.MiddleOut import MiddleOut
from middleout.EntropyEncoder import *

import matplotlib.pyplot as plt

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
    start_time = time.time()

    partitions = split_file(bytes_of_file, chunksize=len(bytes_of_file))
    total_size = 0
    pbar = tqdm(partitions, desc='running middle-out compression scheme')
    bz2test, lz4test, lzmatest, motest = None, None, None, None
    for p in pbar:
        bz2test = bz2compressor(p)
        lz4test = lz4compressor(p)
        lzmatest = lzmacompressor(p)

        mo_compressed = MiddleOut.middle_out(p, size=4)
        pad = pad_stream(len(mo_compressed))
        num_padded = convertBin(pad, bits=4)
        mo_compressed += ('0' * pad) + num_padded
        motest = positiveInt_list(mo_compressed)

    print('original file size:', len(bytes_of_file))
    compressors = ('bz2', 'lz4', 'lzma', 'mo')
    performance = (len(bz2test), len(lz4test), len(lzmatest), len(motest))

    for i, v in zip(compressors, performance):
        print(str(i + ':'), v, '------->', str(100 * v / len(bytes_of_file)), '%')

    print("--- %s seconds ---" % (time.time() - start_time))
