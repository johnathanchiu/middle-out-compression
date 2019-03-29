import collections
import imageio
import time

import argparse

from middleOut.utils import *
from middleOut.middleout import *


def compress_image(image, file_name):

    def compress(image, debug=False, c_layer=False):
        image = image.copy().astype(float)
        compressed_data = array.array('b', [])
        ext = compressed_data.extend
        if debug: print(image); print()
        list_of_patches = split(matrix_multiple_of_eight(image) - 128, 8, 8)
        if debug:
            for x in list_of_patches:
                ext(capture(zig_zag(quantize(dct_2d(x, True), debug=True, c_layer=c_layer), debug=True),
                            c_layer=c_layer))
        else:
            for x in list_of_patches:
                ext(capture(zig_zag(quantize(dct_2d(x), c_layer=c_layer)), c_layer=c_layer))
        if debug: print("compressed data: ", compressed_data); print()
        print(len(compressed_data), sys.getsizeof(compressed_data));
        print()
        return compressed_data

    def compress_ac(values):
        values_bin = MiddleOutUtils.convertBin(values)
        print(len(values_bin))
        compressed = ''
        for x in range(0, len(values_bin), 2000):
            partition = values_bin[x:x+2000]
            part, uncomp_part = MiddleOut.pop_zero_one(partition)
            compressed += part
        print(len(compressed))
        return compressed

    def reduce_entropy(values):
        values_bin = MiddleOutUtils.convertBin(values)
        run_encoded = EntropyReduction.rle(values_bin)
        return run_encoded

    o_length, o_width = image[:, :, 0].shape
    print(o_length, o_width); print()
    YCBCR = rgb2ycbcr(image)

    # Y, Cb, Cr = (YCBCR[:, :, 0])[:o_length, :o_width],\
    #             (YCBCR[:, :, 1])[:o_length, :o_width],\
    #             (YCBCR[:, :, 2])[:o_length, :o_width]
    Y, Cb, Cr = (YCBCR[:, :, 0])[1000:1128, 1000:1128], \
                (YCBCR[:, :, 1])[1000:1128, 1000:1128], \
                (YCBCR[:, :, 2])[1000:1128, 1000:1128]

    p_length, p_width = calc_matrix_eight_size(Y)
    b_lengths, b_width = int(p_length / 8), int(p_width / 8)

    print(p_length, p_width); print()

    compressedY, compressedCb, compressedCr = compress(Y, debug=False), \
                                              compress(Cb, debug=False, c_layer=True), \
                                              compress(Cr, debug=False, c_layer=True)

    # array.array('b', [p_length]) + array.array('b', [p_width])
    compressed = compressedY
    print(len(compressed) * 8)
    entropy_comp(compressed, file_name)

    compress_ac(compressed)

if __name__ == '__main__':
    start_time = time.time()
    print(start_time); print()
    root_path = '/Users/johnathanchiu/Documents/CompressionPics/'  # enter file path of image
    # ap = argparse.ArgumentParser()
    # ap.add_argument("-i", "--image", required=True,
    #                 help="image name")
    # ap.add_argument("-c", "--compressed", required=True,
    #                 help="compressed file name")
    # args = vars(ap.parse_args())
    image_name, compressed_file = 'IMG_0104.jpg', "test"  # input("image name: "), input("compress file name: ")
    # image_name, compressed_file = args["image"], args["compressed"]
    # compressed_file_name = root_path + "compressed/fileSizes/" + compressed_file
    compressed_file_name = compressed_file
    image = imageio.imread(root_path + "tests/" + image_name)
    compress_image(image, compressed_file_name)
    print("--- %s seconds ---" % (time.time() - start_time))

