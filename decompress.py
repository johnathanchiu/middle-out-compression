import imageio
from PIL import Image

from scipy import *
import numpy as np
import struct

import time
import sys
import os

import argparse

from middleOut.utils import *
from middleOut.MiddleOut import MiddleOut


def decompress_image(file_name):

    def decompress(input, dimx=0, dimy=0, debug=False, c_layer=False):
        input = np.asarray(list(input))
        if c_layer:
            compressed_split = [input[i:i + 4] for i in range(0, len(input), 4)]
        else:
            compressed_split = [input[i:i + 8] for i in range(0, len(input), 8)]
        if debug: print(compressed_split); print()
        if debug:
            image_partitions = [idct_2d(undo_quantize(zig_zag_reverse(rebuild(x)), debug=True,
                                                      c_layer=c_layer), debug=True) for x in compressed_split]
        else:
            image_partitions = [idct_2d(undo_quantize(zig_zag_reverse(rebuild(x)),
                                                      c_layer=c_layer)) for x in compressed_split]
        if debug: print(image_partitions); print()
        image = merge_blocks(image_partitions, dimx, dimy)
        if debug: print(image); print()
        if debug: print("image: ", np.round(image + 128))
        return image + 128
    decompressed = entropy_decomp(file_name)

    p_length, p_width = decompressed[:1] * 64, decompressed[1:2] * 64
    no_of_values, no_of_values_cr = int((p_length * p_width) / 8), int((p_length * p_width) / 16)

    return
    #
    #
    # compressedY, compressedCb, compressedCr = result_bytes[:no_of_values], \
    #                                           result_bytes[no_of_values:no_of_values+no_of_values_cr], \
    #                                           result_bytes[no_of_values+no_of_values_cr:]
    #
    # newY, newCb, newCr = decompress(compressedY, dimx=lengths, dimy=widths, debug=False), \
    #                      decompress(compressedCb, dimx=lengths, dimy=widths, debug=False, c_layer=True), \
    #                      decompress(compressedCr, dimx=lengths, dimy=widths, debug=False, c_layer=True)
    #
    # rgbArray = np.flip(
    #     ycbcr2rgb(np.array([newY[0:length, 0:width], newCb[0:length, 0:width], newCr[0:length, 0:width]]).T), axis=1)
    #
    # img = Image.fromarray(rgbArray)
    # img.save(image_save, "PNG", optimize=True)


if __name__ == '__main__':
    start_time = time.time()
    print(start_time); print()
    root_path = '/Users/johnathanchiu/Documents/CompressionPics/'  # enter file path of image
    ap = argparse.ArgumentParser()
    ap.add_argument("-c", "--compressed", required=True,
                    help="compressed file name")
    ap.add_argument("-d", "--decompressed", required=True,
                    help="decompressed image")
    args = vars(ap.parse_args())
    compressed_file, decompressed_image = args[0], args[1]
    image_save = root_path + "compressed/test\ cases" + decompressed_image + ".png"
    compressed_file_name = root_path + "compressed/fileSizes/" + compressed_file
    decompress_image(compressed_file_name)
    print("--- %s seconds ---" % (time.time() - start_time))