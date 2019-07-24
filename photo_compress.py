from middleout.utils import *
from middleout.entropy_encoders import *
from middleout.MiddleOut import MiddleOut
from middleout.utils import writeFile, pad_stream
from jpeg.utils import *

from skimage.measure._structural_similarity import compare_ssim as ssim

from tqdm import tqdm
import argparse
import random
import math

import imageio
import array

from multiprocessing import Pool
import time
import os


SAMPLE_AREA = 256
TABLE, QUALITY, SAMPLE_RATIO = QUANTIZATIONTABLE, 64, 1.0


def jpeg(partition):
    return capture(zig_zag(quantize(dct_2d(partition), table=TABLE)), values=QUALITY, sample_percentage=SAMPLE_RATIO)


def SSIM(photo, photo_x, photo_y, area=200, table=QUANTIZATIONTABLE, resample=False):
    if resample: print(); print("Resampling with new area, previous patch was bad")
    assert photo_x >= 64 or photo_y >= 64, "Photo too small to run SSIM metric, compression diverges"
    assert area % 8 == 0, "Invalid sampling area make sure sample area is equally divisible by 8"
    grab_x, grab_y = int(photo_x // random.uniform(1.5, 4)), int(photo_y // random.uniform(1.5, 4))
    original_sample = np.array(photo[grab_x:grab_x + area, grab_y:grab_y + area], dtype=np.int16)
    pbar = tqdm(range(8, 64))
    last_metric, rep = 0, 0
    for i in pbar:
        compressed_data, partitions = array.array('b', []), []
        ext = compressed_data.extend; app = partitions.append
        pbar.set_description("Running SSIM metric quality, 8 through 64 sampled weights")
        list_of_patches = split((original_sample.copy() - 128).astype(np.int8), 8, 8)
        [ext(capture(zig_zag(quantize(dct_2d(x), table=table)), values=i)) for x in list_of_patches]
        compressed_split = [compressed_data[z:z + i] for z in range(0, len(compressed_data), i)]
        [app(idct_2d(undo_quantize(zig_zag_reverse(rebuild(y)), table=table)) + 128) for y in compressed_split]
        index = merge_blocks(partitions, int(area/8), int(area/8)).astype(np.uint8)
        metric = ssim(original_sample, index, data_range=index.max() - index.min())
        if math.isnan(metric): return SSIM(photo, photo_x, photo_y, area=area, resample=True)
        if metric < 0.7:
            return SSIM(photo, photo_x, photo_y, area=area, table=np.round(table/1.1), resample=True)
        if metric > 0.98:
            if table[0][0] < 8: table[0][0] = 8
            if i % 2 != 0: i += 1
            return i, metric, table
        if abs(last_metric - metric) < 0.0000000001:
            if metric > 0.90:
                if table[0][0] < 8: table[0][0] = 8
                if i % 2 != 0: i += 1
                return i - rep, metric, table
            return SSIM(photo, photo_x, photo_y, area=area, table=np.round(table/1.1), resample=True)
        rep += 1
        if rep == 4: last_metric = metric; rep = 0
    if metric < 0.90:
        return SSIM(photo, photo_x, photo_y, area=area, table=np.round(table/1.2), resample=True)
    if table[0][0] < 8: table[0][0] = 8
    return 64, metric, table


def precompression_factors(image):
    sample = image[:,:,0]
    c_length, c_width = sample.shape
    p_length, p_width = calc_matrix_eight_size(sample)
    return c_length, c_width, p_length, p_width


def convert_sample(img, length, width):
    pbar = tqdm(range(1), desc='Converting image sample space RGB -> YCbCr')
    for _ in pbar: YCBCR = rgb2ycbcr(img)
    y, cb, cr = (YCBCR[:, :, 0])[:length, :width], (YCBCR[:, :, 1])[:length, :width], (YCBCR[:, :, 2])[:length, :width]
    return y.astype(np.int16), cb.astype(np.int16), cr.astype(np.int16)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('-i', "--image", required=True, help="Image name with path")
    ap.add_argument('-c', "--compressed", default='./', help="Folder to save compressed file")
    args = ap.parse_args()
    image_path, compressed = args.image, args.compressed
    _, tail = os.path.split(image_path)
    image = imageio.imread(image_path)
    length, width = image[:, :, 0].shape; c_l, c_w, p_l, p_w = precompression_factors(image)
    y, cb, cr = convert_sample(image, length, width)
    # values_to_keep, metric, quant = SSIM(y, p_l, p_w, area=SAMPLE_AREA, table=QUANTIZATIONTABLE)
    values_to_keep, metric, quant = 16, 0.90, QUANTIZATIONTABLE // 2
    print('Number of samples (out of 64) to keep at metric ' + str(metric) + ': ', values_to_keep)

    keep = [values_to_keep]; padding = [p_l - c_l, p_w - c_w]
    dimensions = convertBin(p_l, bits=16) + convertBin(p_w, bits=16)
    p_length = [convertInt(dimensions[:8], bits=8), convertInt(dimensions[8:16], bits=8)]
    p_width = [convertInt(dimensions[16:24], bits=8), convertInt(dimensions[24:32], bits=8)]

    Y = tqdm(split((matrix_multiple_of_eight(y - 128)).astype(np.int8), 8, 8),
             desc='Running modified jpeg compression 1/3')
    CB = tqdm(split((matrix_multiple_of_eight(cb - 128)).astype(np.int8), 8, 8),
              desc='Running modified jpeg compression 2/3')
    CR = tqdm(split((matrix_multiple_of_eight(cr - 128)).astype(np.int8), 8, 8),
              desc='Running modified jpeg compression 3/3')

    start_time = time.time()
    QUALITY, TABLE = values_to_keep, quant
    with Pool(8) as p: compressed_y = array.array('b', np.asarray(p.map(jpeg, Y)).flatten())
    TABLE = CHROMQUANTIZATIONTABLE
    with Pool(8) as p:
        compressed_cb = array.array('b', np.asarray(p.map(jpeg, CB)).flatten())
        compressed_cr = array.array('b', np.asarray(p.map(jpeg, CR)).flatten())

    q, qc = quant.flatten(), CHROMQUANTIZATIONTABLE.flatten()
    quantization_tables = array.array('b', q) + array.array('b', qc)
    dim = array.array('b', keep) + array.array('b', p_length) + array.array('b', p_width) + array.array('b', padding)
    compressed_data = quantization_tables + dim + compressed_y + compressed_cb + compressed_cr
    compressed_data = [i+128 for i in compressed_data]

    pbar = tqdm(range(1), desc='Writing file with entropy compressor')
    for _ in pbar:
        mo_compressed = MiddleOut.middle_out(compressed_data, size=3)
        pad = pad_stream(len(mo_compressed))
        num_padded = convertBin(pad, bits=4)
        mo_compressed += ('0' * pad) + num_padded
        writeFile(mo_compressed, fileName=compressed+os.path.splitext(tail)[0])
        compressed_data = positiveInt_list(mo_compressed)

    compressed_file = compressed+os.path.splitext(tail)[0]+'.bin'
    compressed_size = os.stat(compressed_file).st_size
    file_size = os.stat(image_path).st_size
    print()
    print("file size after (entropy) compression: ", compressed_size)
    print("file reduction percentage (new file size / old file size): ", (compressed_size / file_size) * 100, "%")
    print("compression converges, new file name: ", compressed_file)
    print("--- %s seconds ---" % (time.time() - start_time))

