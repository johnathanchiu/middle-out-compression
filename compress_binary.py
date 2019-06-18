from middleOut.utils import readFileBytes, writeFile, size_of_file, pad_stream, convertBin
from middleOut.MiddleOut import MiddleOut
from middleOut.EntropyReduction import EntropyReduction

import array

from tqdm import tqdm
import time

if __name__ == '__main__':
    file_name = input("file name: ")
    compressed_file = input("name of compressed file: ")
    bytes_of_file = readFileBytes(file_name)
    bytes_of_file = array.array('b', [b - 128 for b in bytes_of_file])
    start_time = time.time()

    pbar = tqdm(range(1))
    for _ in pbar:
        pbar.set_description("running middle-out compression scheme")
        mo_compressed = MiddleOut.middle_out(bytes_of_file)
        pad = pad_stream(len(mo_compressed))
        num_padded = convertBin(pad, bits=4)
        writeFile(mo_compressed + ('0' * pad) + num_padded, fileName=compressed_file)

    print("compression converges!")
    compressed_size = size_of_file(compressed_file + '.bin')
    print("size of resulting file:", compressed_size)
    print("compression percentage (compressed / original): ", compressed_size / size_of_file(file_name) * 100, "%")
    print("--- %s seconds ---" % (time.time() - start_time))
