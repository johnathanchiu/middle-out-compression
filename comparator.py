# This program produces the results of compression on a specific file
# © Johnathan Chiu, 2019

from middleout.utils import *
from middleout.MiddleOut import MiddleOut
from middleout.entropy_encoders import *

from tqdm import tqdm
import argparse
import time
import os


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('-o', "--original", required=True, help="Path to file")
    ap.add_argument('-c', "--compressed", required=False, default="./",
                    help="Dir. to save file to")
    ap.add_argument('-s', "--size", required=False, type=int, default=2, help="Library size to use")
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
        gziptest = gzipcompressor(p)

        mo_compressed = MiddleOut.middle_out(gziptest, size=0)
        pad = pad_stream(len(mo_compressed))
        num_padded = convertBin(pad, bits=4)
        mo_compressed += ('0' * pad) + num_padded
        motest = positiveInt_list(mo_compressed)

    print('original file size:', len(bytes_of_file))
    compressors = ('bz2', 'gzip', 'lz4', 'lzma', 'mo')
    performance = (len(bz2test), len(gziptest), len(lz4test), len(lzmatest), len(motest))

    for i, v in zip(compressors, performance):
        print(str(i + ':'), v, '------->', str(100 * v / len(bytes_of_file)), '%')

    print("--- %s seconds ---" % (time.time() - start_time))
