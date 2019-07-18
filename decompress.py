from middleOut.MiddleOut import MiddleOut
from middleOut.utils import readFile, writeFileBytes, remove_padding

import array
import os

import argparse
from tqdm import tqdm
import time

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('-c', "--compressed", required=True, help="Path to compressed file")
    ap.add_argument('-p', "--path", required=False, default='./', help="Path to save the decompressed file")
    args = ap.parse_args()
    compressed_file = args.compressed
    decompressed = args.path + os.path.splitext(os.path.basename(compressed_file))[0]
    start_time = time.time()

    pbar = tqdm(range(1))
    for _ in pbar:
        pbar.set_description("running middle-out decompression scheme")
        bitstream = remove_padding(readFile(compressed_file))
        decomp = array.array('B', [b+128 for b in array.array('b', MiddleOut.middle_out_decompress(bitstream))])
        writeFileBytes(decomp, decompressed)

    print("file saved to:", decompressed)
    print("decompression converges!")
    print("--- %s seconds ---" % (time.time() - start_time))