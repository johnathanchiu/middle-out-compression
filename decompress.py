import imageio
from PIL import Image

from scipy import *
import numpy as np
import struct

from tqdm import tqdm
import time
import sys
import os

import argparse

from middleOut.utils import *
from middleOut.EntropyReduction import *
from middleOut.MiddleOut import *


def decompress_image(file_name):

    def decompress(input, dimx=0, dimy=0, debug=False, c_layer=False):
        input = np.asarray(list(input))
        if c_layer:
            compressed_split = [input[i:i + 4] for i in range(0, len(input), 4)]
        else:
            compressed_split = [input[i:i + 8] for i in range(0, len(input), 8)]
        image_partitions = []
        pbar = tqdm(compressed_split)
        append = image_partitions.append
        if debug: print(compressed_split); print()
        if debug:
            for x in compressed_split:
                idct_2d(undo_quantize(zig_zag_reverse(rebuild(x)), debug=True, c_layer=c_layer), debug=True)
        else:
            for x in pbar:
                pbar.set_description("Running modified jpeg decompression")
                append(idct_2d(undo_quantize(zig_zag_reverse(rebuild(x)), c_layer=c_layer)))
        if debug: print(image_partitions); print()
        pbar2 = tqdm(range(1))
        for _ in pbar2:
            pbar2.set_description("Merging blocks back to form whole image")
            image = merge_blocks(image_partitions, dimx, dimy)
        if debug: print(image); print()
        if debug: print("image: ", np.round(image + 128))
        return image + 128

    def decompress_bitset(bitset):
        decompressed = MiddleOut.decompressStream(bitset)
        return MiddleOutUtils.convertInt_list(decompressed)

    # compressed_bitset = readFile()
    pbar = tqdm(range(1))
    for _ in pbar:
        pbar.set_description("Reading bits from file using entropy decompressor")
        compressed_bitset = EntropyReduction.bz2_unc(file_name)

    # p_length, p_width = MiddleOutUtils.convertInt(compressed_bitset[:16], bits=16), \
    #                     MiddleOutUtils.convertInt(compressed_bitset[16:32], bits=16)

    p_length = MiddleOutUtils.convertInt(MiddleOutUtils.convertBin(compressed_bitset[0], bits=8) +
                                         MiddleOutUtils.convertBin(compressed_bitset[1], bits=8), bits=16)
    p_width = MiddleOutUtils.convertInt(MiddleOutUtils.convertBin(compressed_bitset[2], bits=8) +
                                         MiddleOutUtils.convertBin(compressed_bitset[3], bits=8), bits=16)

    s_length, s_width = int(p_length / 8), int(p_width / 8)
    # length, width = p_length - MiddleOutUtils.convertInt(compressed_bitset[32:40], bits=8), \
    #                 p_width - MiddleOutUtils.convertInt(compressed_bitset[40:48], bits=8)
    length, width = p_length - compressed_bitset[4], p_width - compressed_bitset[5]

    result_bytes = compressed_bitset[6:]
    # result_bytes = decompress_bitset(compressed_bitset[48:])

    no_of_values, no_of_values_cr = int((p_length * p_width) / 8), int((p_length * p_width) / 16)

    compressedY, compressedCb, compressedCr = result_bytes[:no_of_values], \
                                              result_bytes[no_of_values:no_of_values+no_of_values_cr], \
                                              result_bytes[no_of_values+no_of_values_cr:]

    newY, newCb, newCr = decompress(compressedY, dimx=s_length, dimy=s_width, debug=False), \
                         decompress(compressedCb, dimx=s_length, dimy=s_width, debug=False, c_layer=True), \
                         decompress(compressedCr, dimx=s_length, dimy=s_width, debug=False, c_layer=True)

    pbar = tqdm(range(1))
    for _ in pbar:
        pbar.set_description("Converting image sample space YCbCr -> RGB")
        rgbArray = np.flip(ycbcr2rgb(np.array([newY[0:length, 0:width], newCb[0:length, 0:width],
                                newCr[0:length, 0:width]]).T), axis=1)

    img = Image.fromarray(rgbArray)
    img.save(image_save, "PNG", optimize=True)


if __name__ == '__main__':
    start_time = time.time()
    # print(start_time); print()
    root_path = '/Users/johnathanchiu/Documents/CompressionPics/'  # enter file path of image
    # ap = argparse.ArgumentParser()
    # ap.add_argument("-c", "--compressed", required=True,
    #                 help="compressed file name")
    # ap.add_argument("-d", "--decompressed", required=True,
    #                 help="decompressed image")
    # args = vars(ap.parse_args())
    # compressed_file, decompressed_image = args[0], args[1]
    compressed_file, decompressed_image = input("compressed file path without extension: "), \
                                          input("Name of decompressed image without extension: ")
    print();
    image_save = root_path + "compressed/testCases/" + decompressed_image + ".png"
    compressed_file_name = root_path + "compressed/fileSizes/" + compressed_file
    decompress_image(compressed_file_name)
    print(); print("decompression converged, your file is at: ", image_save)
    print("--- %s seconds ---" % (time.time() - start_time))
