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
    bytes_of_file = read_file_bytes(file_name)
    start_time = time.time()

    partitions = split_file(bytes_of_file, chunksize=len(bytes_of_file))
    total_size = 0
    pbar = tqdm(partitions, desc='running compression scheme(s)')
    bz2test, gziptest, lz4test, lzmatest, motest = None, None, None, None, None
    for p in pbar:
        bz2test = bz2compressor(p)
        lz4test = lz4compressor(p)
        lzmatest = lzmacompressor(p)
        gziptest = gzipcompressor(p)
        brotlitest = brotlicompressor(p)
        zstdtest = zstdcompressor(p)
        motest = MiddleOut.compress(lz4test)

    print('original file size:', len(bytes_of_file))
    compressors = ('bz2', 'gzip', 'lz4', 'lzma', 'brotli', 'zstd', 'mo')
    performance = (len(bz2test), len(gziptest), len(lz4test), len(lzmatest),
                   len(brotlitest), len(zstdtest), len(motest))

    for i, v in zip(compressors, performance):
        print(str(i + ':'), v, '------->', str(100 * v / len(bytes_of_file)), '%')

    print("--- %s seconds ---" % (time.time() - start_time))
