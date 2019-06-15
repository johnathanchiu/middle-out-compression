from middleOut.MiddleOut import MiddleOut
from middleOut.utils import readFile, writeFile, remove_padding

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
        writeFile(MiddleOut.middle_out_decompress(bitstream), decompressed_file_name)

    print("decompression converges!")
    print("--- %s seconds ---" % (time.time() - start_time))
