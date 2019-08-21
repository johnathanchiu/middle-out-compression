# This program produces the results of compression on a specific file
# © Johnathan Chiu, 2019

from middleout.middle_out import MiddleOut
from middleout.entropy_encoders import *
from middleout.huffman import *

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
    original = bytes_of_file
    start_time = time.time()

    sizes = []
    partitions = [bz2compressor, gzipcompressor, lz4compressor, lzmacompressor, brotlicompressor, zstdcompressor]
    pbar = tqdm(partitions, desc='running compression scheme(s)')
    for p in pbar:
        sizes.append(p(bytes_of_file))
    frame = Huffman()
    bytes_of_file = lz4compressor(bytes_of_file)
    sizes.append(MiddleOut.compress(bytes_of_file, stride=16384 * 2, distance=17))

    print('original file size:', len(original))
    compressors = ['bz2', 'gzip', 'lz4', 'lzma', 'brotli', 'zstd', 'mo']
    performance = [len(c) for c in sizes]

    for i, v in zip(compressors, performance):
        print(str(i + ':'), v, '------->', str(100 * v / len(original)), '%')

    print("--- %s seconds ---" % (time.time() - start_time))
