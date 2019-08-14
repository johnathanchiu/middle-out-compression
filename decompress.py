from middleout.MiddleOut import MiddleOut
from middleout.entropy_encoders import *
from middleout.utils import *

import os

import argparse
import time

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('-c', "--compressed", required=True, help="Path to compressed file")
    ap.add_argument('-p', "--path", required=False, default='./', help="Path to save the decompressed file")
    args = ap.parse_args()
    compressed_file = args.compressed
    decompressed = args.path + os.path.splitext(os.path.basename(compressed_file))[0]
    start_time = time.time()

    bit_stream = read_file_bits(compressed_file)
    decompressed_mo = MiddleOut.decompress(bit_stream)
    file_bytes = lz4decompressor(decompressed_mo)
    # file_bytes = decompressed_mo
    write_file_bytes(file_bytes, decompressed)

    print("file saved to:", decompressed)
    print("decompression converges!")
    print("--- %s seconds ---" % (time.time() - start_time))
