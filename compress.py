from middleOut.EntropyReduction import *
from middleOut.MiddleOut import *
from middleOut.utils import *

from tqdm import tqdm
from tqdm import trange

import collections
import imageio
import array

import argparse
import time


def compress_image(image, file_name):

    def compress(image, debug=False, c_layer=False):
        image = image.copy().astype(float)
        compressed_data = array.array('b', [])
        ext = compressed_data.extend
        if debug: print(image); print()
        list_of_patches = split(matrix_multiple_of_eight(image) - 128, 8, 8)
        pbar = tqdm(list_of_patches)
        if debug:
            for x in list_of_patches:
                ext(capture(zig_zag(quantize(dct_2d(x, True), debug=True, c_layer=c_layer), debug=True),
                            c_layer=c_layer))
        else:
            for x in pbar:
                pbar.set_description("Running modified jpeg compression")
                ext(capture(zig_zag(quantize(dct_2d(x), c_layer=c_layer)), c_layer=c_layer))
        if debug: print("compressed data: ", compressed_data); print()
        return compressed_data

    def middleout(values):
        values_bin = MiddleOutUtils.convertBin_list(values)
        print(values)
        compressed = ''
        pbar = tqdm(range(0, len(values_bin), 100000))
        for x in pbar:
            pbar.set_description("Running middle-out compression")
            curr_stream = values_bin[x:x+100000]
            compressed_bitset = MiddleOut.middle_out(curr_stream)
            compressed += compressed_bitset
        return compressed

    o_length, o_width = image[:, :, 0].shape
    # print()
    # print("original file dimensions: ", o_length, o_width); print()

    pbar = tqdm(range(1))
    for _ in pbar:
        pbar.set_description("Converting image sample space RGB -> YCbCr")
        YCBCR = rgb2ycbcr(image)

    Y, Cb, Cr = (YCBCR[:, :, 0])[:o_length, :o_width],\
                (YCBCR[:, :, 1])[:o_length, :o_width],\
                (YCBCR[:, :, 2])[:o_length, :o_width]

    c_length, c_width = Y.shape
    p_length, p_width = calc_matrix_eight_size(Y)
    # print("padded image dimensions: ", p_length, p_width); print()
    dimensions = MiddleOutUtils.convertBin(p_length, bits=16) + MiddleOutUtils.convertBin(p_width, bits=16)
    padding = [p_length - c_length, p_width - c_width]
    p_length = [MiddleOutUtils.convertInt(dimensions[:8], bits=8),
                MiddleOutUtils.convertInt(dimensions[8:16], bits=8)]
    p_width = [MiddleOutUtils.convertInt(dimensions[16:24], bits=8),
               MiddleOutUtils.convertInt(dimensions[24:32], bits=8)]

    # padding = MiddleOutUtils.convertBin(p_length - c_length, bits=8) + \
    #           MiddleOutUtils.convertBin(p_length - c_width, bits=8)

    compressedY = compress(Y, debug=False)
    compressedCb = compress(Cb, debug=False, c_layer=True)
    compressedCr = compress(Cr, debug=False, c_layer=True)

    dim = array.array('b', p_length) + array.array('b', p_width) + array.array('b', padding)
    compressed = dim + compressedY + compressedCb + compressedCr
    pbar = tqdm(range(1))
    for _ in pbar:
        pbar.set_description("writing file with entropy compressor")
        orig_size, size, filename = EntropyReduction.bz2(compressed, file_name)

    return orig_size, size, filename

    # compress_bitset_y = middleout(compressedY)
    # compress_bitset_cb = middleout(compressedCb)
    # compress_bitset_cr = middleout(compressedCr)

    # bit_file = dimensions + padding + compress_bitset_y + compress_bitset_cb + compress_bitset_cr
    # appended_bits = len(bit_file) - (len(bit_file) % 8)
    # bit_file += MiddleOutUtils.convertBin(appended_bits, bits=3)
    # size = len(bit_file)
    # writeFile(bit_file)


if __name__ == '__main__':
    start_time = time.time()
    # print(start_time); print()
    root_path = '/Users/johnathanchiu/Documents/CompressionPics/'  # enter file path of image
    # ap = argparse.ArgumentParser()
    # ap.add_argument("-i", "--image", required=True,
    #                 help="image name")
    # ap.add_argument("-c", "--compressed", required=True,
    #                 help="compressed file name")
    # args = vars(ap.parse_args())
    image_name, compressed_file = input("Image path: "), input("Compressed file name: ")
    # image_name, compressed_file = args["image"], args["compressed"]
    # compressed_file_name = root_path + "compressed/fileSizes/" + compressed_file
    compressed_file_name = root_path + 'compressed/' + 'fileSizes/' + compressed_file
    image = imageio.imread(root_path + "tests/" + image_name)
    file_size, size, filename = compress_image(image, compressed_file_name)
    print()
    print("file size after (entropy) compression: ", size)
    print("file reduction percentage: ", (1 - (size / file_size)) * 100, "%")
    print("compression converges, new file name: ", filename)
    print("--- %s seconds ---" % (time.time() - start_time))

