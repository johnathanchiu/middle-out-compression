from PIL import Image

from scipy.ndimage import *

from tqdm import tqdm
import time

from JPEG.utils import *
from middleOut.utils import *
from middleOut.EntropyReduction import EntropyReduction


def decompress_image(file_name):

    def decompress(input, dimx=0, dimy=0, qual=64, c_layer=False, count=1, debug=False):
        if c_layer:
            compressed_split = np.array([np.array(input[i:i+int(qual * 1 / 2)], dtype=np.int8)
                                         for i in range(0, len(input), int(qual * 1 / 2))], dtype=np.int8)
        else:
            compressed_split = np.array([np.array(input[i:i+qual], dtype=np.int8)
                                         for i in range(0, len(input), qual)], dtype=np.int8)
        image_partitions = []
        append = image_partitions.append
        pbar = tqdm(compressed_split)
        if debug: print(compressed_split); print()
        if debug:
            for x in compressed_split:
                append(idct_2d(undo_quantize(zig_zag_reverse(rebuild(x)), debug=True, c_layer=c_layer), debug=True))
        else:
            for x in pbar:
                descrip = "Running modified jpeg decompression " + str(count) + " / 3"
                pbar.set_description(descrip)
                append(idct_2d(undo_quantize(zig_zag_reverse(rebuild(x)), c_layer=c_layer)))
        if debug: print(image_partitions); print()
        pbar_2 = tqdm(range(1))
        for _ in pbar_2:
            pbar_2.set_description("Merging blocks back to form whole image")
            image = merge_blocks(image_partitions, dimx, dimy)
        if debug: print(image); print()
        if debug: print("image: ", np.round(image + 128))
        return image + 128

    pbar_1 = tqdm(range(1))
    for _ in pbar_1:
        pbar_1.set_description("Reading bits from file using entropy decompressor")
        compressed_bitset = EntropyReduction.bz2_unc(file_name)

    quality_metric = compressed_bitset[0]
    p_length = convertInt(convertBin(compressed_bitset[1], bits=8) + convertBin(compressed_bitset[2], bits=8), bits=16)
    p_width = convertInt(convertBin(compressed_bitset[3], bits=8) + convertBin(compressed_bitset[4], bits=8), bits=16)
    s_length, s_width = int(p_length / 8), int(p_width / 8)
    length, width = p_length - compressed_bitset[5], p_width - compressed_bitset[6]

    result_bytes = compressed_bitset[7:]
    no_of_values, no_of_values_cr = int((p_length * p_width) / 64 * quality_metric), \
                                    int((p_length * p_width) / 64 * (int(quality_metric * 1 / 2)))

    compressedY = result_bytes[:no_of_values]
    compressedCb = result_bytes[no_of_values:no_of_values+no_of_values_cr]
    compressedCr = result_bytes[no_of_values+no_of_values_cr:no_of_values+(2*no_of_values_cr)]

    newY = decompress(compressedY, dimx=s_length, dimy=s_width, qual=quality_metric, c_layer=False, count=1)
    newCb = decompress(compressedCb, dimx=s_length, dimy=s_width, qual=quality_metric, c_layer=True, count=2)
    newCr = decompress(compressedCr, dimx=s_length, dimy=s_width, qual=quality_metric, c_layer=True, count=3)

    pbar_2 = tqdm(range(1))
    for _ in pbar_2:
        pbar_2.set_description("Converting image sample space YCbCr -> RGB")
        YCBCR = np.array([newY[0:length, 0:width], newCb[0:length, 0:width], newCr[0:length, 0:width]]).T
        rgbArray = ycbcr2rgb(np.flip(YCBCR, axis=1))
        rgbArray = rotate(rgbArray, 90)

    img = Image.fromarray(rgbArray)
    img.save(image_save, "JPEG", optimize=True)


if __name__ == '__main__':
    # print(start_time); print()
    root_path = None  # set root directory of project file
    # ap = argparse.ArgumentParser()
    # ap.add_argument("-c", "--compressed", required=True,
    #                 help="compressed file name")
    # ap.add_argument("-d", "--decompressed", required=True,
    #                 help="decompressed image")
    # args = vars(ap.parse_args())
    # compressed_file, decompressed_image = args[0], args[1]
    if root_path is None:
        compressed_file = input("Compressed file path without extension (You can set a root directory in the code): ")
        decompressed_image = input("Name of decompressed image without extension (You can set a root directory in the code): ")
        image_save = decompressed_image + ".png"
        compressed_file_name = compressed_file
    else:
        compressed_file, decompressed_image = input("Compressed file path without extension: "), \
                                              input("Name of decompressed image without extension: ")
        image_save = decompressed_image + ".png"
        compressed_file_name = root_path + compressed_file
    print();
    start_time = time.time()
    decompress_image(compressed_file_name)
    print(); print("Decompression converged, your file is at: ", image_save)
    print("--- %s seconds ---" % (time.time() - start_time))
