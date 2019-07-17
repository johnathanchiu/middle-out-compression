from JPEG.utils import *
from middleOut.utils import convertInt, convertBin, writeFile, pad_stream
from middleOut.MiddleOut import MiddleOut

from skimage.measure._structural_similarity import compare_ssim as ssim

from tqdm import tqdm
import argparse
import random

import imageio
import array
import os

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
                ext((capture(zig_zag(quantize(dct_2d(x, debug=True), debug=True, c_layer=c_layer), debug=True),
                             values=qual, c_layer=c_layer)))
        else:
            for x in pbar:
                descrip = "Running modified jpeg compression " + str(count) + " / 3"
                pbar.set_description(descrip)
                ext((capture(zig_zag(quantize(dct_2d(x), c_layer=c_layer)), values=qual, c_layer=c_layer)))
        if debug: print("compressed data: ", compressed_data); print()
        return compressed_data

    def SSIM(photo, photo_x, photo_y):
        assert photo_x >= 512 or photo_y >= 512, "Photo too small to run SSIM metric, compression diverges"
        grab_x, grab_y = int(photo_x / random.uniform(2, 4)), int(photo_y / random.uniform(2, 4))
        original_sample = np.array(photo[grab_x:grab_x + 176, grab_y:grab_y + 176], dtype=np.int16)
        pbar = tqdm(range(10, 64))
        previous_metric = 0
        for i in pbar:
            compressed_data = array.array('b', [])
            partitions = []
            pbar.set_description("Running SSIM metric quality, 14 through 64 sampled weights")
            list_of_patches = split(original_sample - 128, 8, 8)
            for x in list_of_patches:
                comp = capture(zig_zag(quantize(dct_2d(x))), values=i)
                compressed_data.extend(comp)
            compressed_split = [compressed_data[z:z + i] for z in range(0, len(compressed_data), i)]
            for y in compressed_split:
                samples = idct_2d(undo_quantize(zig_zag_reverse(rebuild(y)))) + 128
                partitions.append(samples)
            index = merge_blocks(partitions, int(176/8), int(176/8))
            metric = ssim(original_sample.flatten(), index.flatten(), data_range=index.max() - index.min())
            if i == 1:
                previous_metric = metric
            else:
                if metric > 0.97 or abs(previous_metric - metric) < 0.00001:
                    return i - 1
                previous_metric = metric
        return 64

    o_length, o_width = image[:, :, 0].shape

    pbar = tqdm(range(1))
    for _ in pbar:
        pbar.set_description("Converting image sample space RGB -> YCbCr")
        YCBCR = rgb2ycbcr(image)

    Y, Cb, Cr = (YCBCR[:, :, 0])[:o_length, :o_width], (YCBCR[:, :, 1])[:o_length, :o_width], \
                (YCBCR[:, :, 2])[:o_length, :o_width]

    c_length, c_width = Y.shape
    p_length, p_width = calc_matrix_eight_size(Y)

    values_to_keep = SSIM(Y, p_length, p_width)
    if values_to_keep % 2 != 0:
        values_to_keep += 1
    print("Number of samples (out of 64) to keep: ", values_to_keep)

    # print("padded image dimensions: ", p_length, p_width); print()
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

    pbar = tqdm(range(1))
    for _ in pbar:
        pbar.set_description("Writing file with middleout")
        mo_compressed = MiddleOut.middle_out(compressed, size=2)
        pad = pad_stream(len(mo_compressed))
        num_padded = convertBin(pad, bits=4)
        mo_compressed += ('0' * pad) + num_padded
        writeFile(mo_compressed, fileName=file_name)

    return len(mo_compressed) // 8, file_name+'.bin'


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('-i', "--image", required=True,
                    help="Image name with path")
    ap.add_argument('-c', "--compressed", default='./',
                    help="Folder to save compressed file")
    args = ap.parse_args()
    image_path, compressed = args.image, args.compressed
    start_time = time.time()
    image = imageio.imread(image_path)
    _, tail = os.path.split(image_path)
    size, filename = compress_image(image, compressed+os.path.splitext(tail)[0])
    file_size = os.stat(image_path).st_size
    print()
    print("file size after (entropy) compression: ", size)
    print("file reduction percentage (new file size / old file size): ", (size / file_size) * 100, "%")
    print("compression converges, new file name: ", filename)
    print("--- %s seconds ---" % (time.time() - start_time))

