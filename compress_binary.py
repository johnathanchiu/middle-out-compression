from middleOut.utils import readFileBytes, writeFile, size_of_file, pad_stream, convertBin
from middleOut.MiddleOut import MiddleOut
from middleOut.EntropyReduction import EntropyReduction

import array
import os

import argparse
from tqdm import tqdm
import time

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('-o', "--original", required=True, help="path to file")
    ap.add_argument("-c", "--compressed", required=False, default="./", help="dir. to save file to")
    args = ap.parse_args()
    file_name = args.original
    compressed_file = args.compressed + os.path.splitext(os.path.basename(file_name))[0]
    bytes_of_file = readFileBytes(file_name)
    bytes_of_file = array.array('b', [b - 128 for b in bytes_of_file])
    start_time = time.time()

    pbar = tqdm(range(1))
    for _ in pbar:
        pbar.set_description("running middle-out compression scheme")
        # bytes_of_file = array.array('b', [b - 128 for b in list(EntropyReduction.lz4_compress(bytes_of_file))])
        # bytes_of_file = array.array('b', EntropyReduction.bz2compressor(bytes_of_file))
        mo_compressed = MiddleOut.middle_out(bytes_of_file, size=2)
        pad = pad_stream(len(mo_compressed))
        num_padded = convertBin(pad, bits=4)
        writeFile(mo_compressed + ('0' * pad) + num_padded, fileName=compressed_file)

    print("compression converges!")
    compressed_size = size_of_file(compressed_file + '.bin')
    print("size of resulting file:", compressed_size)
    print("compression percentage (compressed / original): ", compressed_size / size_of_file(file_name) * 100, "%")
    print("--- %s seconds ---" % (time.time() - start_time))
