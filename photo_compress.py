from JPEG.utils import *
from middleOut.utils import *
from middleOut.MiddleOut import MiddleOut
from  middleOut.EntropyReduction import EntropyReduction

from tqdm import tqdm

import imageio
import array

import time


def compress_image(image, file_name):

    def compress(image, qual=64, count=1, debug=False, c_layer=False):
        image_copy = image.copy().astype(float)
        compressed_data = array.array('b', [])
        ext = compressed_data.extend
        if debug: print(image); print()
        list_of_patches = split((matrix_multiple_of_eight(image_copy) - 128).astype(np.int8), 8, 8)
        pbar = tqdm(list_of_patches)
        if debug:
            for x in list_of_patches:
                ext(capture(zig_zag(quantize(dct_2d(x, debug=True), debug=True, c_layer=c_layer), debug=True), values=qual,
                            c_layer=c_layer))
        else:
            for x in pbar:
                descrip = "Running modified jpeg compression " + str(count) + " / 3"
                pbar.set_description(descrip)
                ext(capture(zig_zag(quantize(dct_2d(x), c_layer=c_layer)), values=qual, c_layer=c_layer))
        if debug: print("compressed data: ", compressed_data); print()
        return compressed_data

    o_length, o_width = image[:, :, 0].shape

    pbar = tqdm(range(1))
    for _ in pbar:
        pbar.set_description("Converting image sample space RGB -> YCbCr")
        YCBCR = rgb2ycbcr(image)

    # Y, Cb, Cr = (YCBCR[:, :, 0])[:o_length, :o_width], (YCBCR[:, :, 1])[:o_length, :o_width], \
    #             (YCBCR[:, :, 2])[:o_length, :o_width]
    Y, Cb, Cr = (YCBCR[:, :, 0])[:1000, :1000], (YCBCR[:, :, 1])[:1000, :1000], \
                (YCBCR[:, :, 2])[:1000, :1000]

    c_length, c_width = Y.shape
    p_length, p_width = calc_matrix_eight_size(Y)

    values_to_keep = 16

    dimensions = convertBin(p_length, bits=16) + convertBin(p_width, bits=16)
    padding = [p_length - c_length, p_width - c_width]
    p_length = [convertInt(dimensions[:8], bits=8), convertInt(dimensions[8:16], bits=8)]
    p_width = [convertInt(dimensions[16:24], bits=8), convertInt(dimensions[24:32], bits=8)]
    keep = [values_to_keep]

    compressedY = compress(Y, qual=values_to_keep, count=1, debug=False)
    compressedCb = compress(Cb, qual=values_to_keep, count=2, debug=False, c_layer=True)
    compressedCr = compress(Cr, qual=values_to_keep, count=3, debug=False, c_layer=True)

    dim = array.array('b', keep) + array.array('b', p_length) + array.array('b', p_width) + array.array('b', padding)
    compressed = dim + compressedY + compressedCb + compressedCr

    pbar_mo = tqdm(range(1))
    for _ in pbar_mo:
        pbar_mo.set_description("running middle out compresssion")
        mo_compressed = MiddleOut.middle_out(compressed, debug=False)
        pad = pad_stream(len(mo_compressed))
        num_padded = convertBin(pad, bits=4)
        mo_compressed = mo_compressed + ('0' * pad) + num_padded

    # pbar = tqdm(range(1))
    # for _ in pbar:
    #     pbar.set_description("writing file with entropy compressor")
    #     size, filename = EntropyReduction.bz2(compressed, file_name)

    # print(); print("size of data:", len(compressed) * 8); print("size of file after middleout",
    #                                                              int(np.round(len(mo_compressed) / 8)))

    return len(compressed), file_name + '.bin', mo_compressed, int(np.round(len(mo_compressed) / 8))
    # return size, filename, None


if __name__ == '__main__':
    # print(start_time); print()
    root_path = '/Users/johnathanchiu/Documents/'
    if root_path is None:
        image_name, compressed_file = input("Image path (You can set a root directory in the code): "), \
                                      input("Compressed file name (whatever you want to name the compressed file): ")
        compressed_file_name = compressed_file
        image = imageio.imread(image_name)
    else:
        image_name, compressed_file = input("Image path: "), \
                                      input("Compressed file name (whatever you want to name the compressed file): ")
        compressed_file_name = root_path + 'middleout/middleoutref/' + compressed_file
        image_name = root_path + 'CompressionPics/tests/' + image_name
        image = imageio.imread(image_name)
    start_time = time.time()
    size, filename, midout, compressed_size = compress_image(image, compressed_file_name)
    writeFile(midout, fileName=compressed_file_name)
    print()
    print("file size after (entropy) compression: ", compressed_size)
    print("lossless reduction percentage (after entropy / before entropy): ", (compressed_size / size) * 100, "%")
    print("compression converges, new file name: ", filename)
    print("--- %s seconds ---" % (time.time() - start_time))

