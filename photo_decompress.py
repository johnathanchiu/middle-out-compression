from middleout.utils import convertInt, convertBin, readFile, remove_padding
from middleout.MiddleOut import MiddleOut
from jpeg.utils import *

from multiprocessing import Pool
from scipy.ndimage import *
import imageio

from tqdm import tqdm
import argparse

import array
import time
import os


SAMPLE_RATIO, TABLE = 1.0, QUANTIZATIONTABLE


def jpeg_decompress(partition):
    return (idct_2d(undo_quantize(zig_zag_reverse(rebuild(partition)), table=TABLE)) + 128).astype(np.uint8)


def image_attributes(compressed):
    table = np.asarray(compressed[:64], dtype=np.float16).reshape(8, 8)
    tablecr = np.asarray(compressed[64:128], dtype=np.float16).reshape(8, 8)
    quality_metric = compressed[128]
    p_length = convertInt(convertBin(compressed[129],bits=8)+convertBin(compressed[130],bits=8),bits=16)
    p_width = convertInt(convertBin(compressed[131],bits=8)+convertBin(compressed[132],bits=8),bits=16)
    length, width = p_length - compressed[133], p_width - compressed[134]
    val, val_cr = int(p_length*p_width / 64*quality_metric), int(p_length*p_width / 64*int(quality_metric*SAMPLE_RATIO))
    return table, tablecr, p_length, p_width, length, width, val, val_cr


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('-c', "--compressed", required=True, help="Compressed file name with path & extension")
    ap.add_argument('-d', "--decompressed", default='./', help="Path to file for decompressed image")
    args = ap.parse_args()
    compressed_file, decompressed_image = args.compressed, args.decompressed
    _, tail = os.path.split(compressed_file)
    image_save = decompressed_image+os.path.splitext(tail)[0]

    start_time = time.time()

    pbar = tqdm(range(1), desc='Reading bits from file using entropy decompressor')
    for _ in pbar:
        bitstream = remove_padding(readFile(compressed_file))
        print('bitstream:', bitstream)
        comp = array.array('b', [i-128 for i in array.array('B', MiddleOut.middle_out_decompress(bitstream))])

    data = comp[135:]
    tab, tabcr, p_length, p_width, length, width, val, val_cr = image_attributes(comp)
    compressedY, compressedCb, compressedCr = data[:val], data[val:val+val_cr], data[val+val_cr:val+(2*val_cr)]

    TABLE = tab
    with Pool(8) as p:
        split_y = [np.array(compressedY[i:i+int(comp[128]*SAMPLE_RATIO)], dtype=np.int8)
                   for i in range(0, len(compressedY), int(comp[128]*SAMPLE_RATIO))]
        split_y = tqdm(split_y, desc='Running modified jpeg decompression 1/3')
        y = merge_blocks(p.map(jpeg_decompress, split_y), int(p_length / 8), int(p_width / 8))
    TABLE = tabcr
    with Pool(8) as p:
        split_cb = [np.array(compressedCb[i:i+int(comp[128]*SAMPLE_RATIO)], dtype=np.int8)
                    for i in range(0, len(compressedCb), int(comp[128]*SAMPLE_RATIO))]
        split_cr = [np.array(compressedCr[i:i+int(comp[128]*SAMPLE_RATIO)], dtype=np.int8)
                    for i in range(0, len(compressedCr), int(comp[128]*SAMPLE_RATIO))]
        split_cb = tqdm(split_cb, desc='Running modified jpeg decompression 2/3')
        split_cr = tqdm(split_cr, desc='Running modified jpeg decompression 3/3')
        cb = merge_blocks(p.map(jpeg_decompress, split_cb), int(p_length / 8), int(p_width / 8))
        cr = merge_blocks(p.map(jpeg_decompress, split_cr), int(p_length / 8), int(p_width / 8))

    rgbArray = None
    pbar = tqdm(range(1), desc='Converting image sample space YCbCr -> RGB')
    for _ in pbar:
        YCBCR = np.array([y[0:length, 0:width], cb[0:length, 0:width], cr[0:length, 0:width]]).T
        rgbArray = ycbcr2rgb(np.flip(YCBCR, axis=1)); rgbArray = rotate(rgbArray, 90)

    imageio.imwrite(image_save, rgbArray, quality=100)
    print(); print("Decompression converged, your file is at: ", image_save)
    print("--- %s seconds ---" % (time.time() - start_time))
