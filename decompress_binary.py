from middleOut.MiddleOut import MiddleOut
from middleOut.utils import readFile, writeFileBytes, remove_padding

import array

from tqdm import tqdm
import time

if __name__ == '__main__':
    compressed_file = input("compressed file with extension: ")
    decompressed_file_name = input("name of decompressed file with extension: ")
    start_time = time.time()

    pbar = tqdm(range(1))
    for _ in pbar:
        pbar.set_description("running middle-out decompression scheme")
        bitstream = remove_padding(readFile(compressed_file))
        decomp = array.array('B', [b+128 for b in array.array('b', MiddleOut.middle_out_decompress(bitstream))])
        writeFileBytes(decomp, decompressed_file_name)

    print("decompression converges!")
    print("--- %s seconds ---" % (time.time() - start_time))
