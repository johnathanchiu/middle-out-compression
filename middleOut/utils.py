from scipy import fftpack
from scipy import *
import numpy as np

from io import StringIO


def split(array, nrows, ncols):
    """Split a matrix into sub-matrices."""
    return [array[x:x + nrows, y:y + ncols] for x in range(0, array.shape[0], nrows) for y in range(0, array.shape[1],
                                                                                                    ncols)]


# converts rgb to ycbcr colorspace
def rgb2ycbcr(im):
    xform = np.array([[.299, .587, .114], [-.1687, -.3313, .5], [.5, -.4187, -.0813]])
    ycbcr = im.dot(xform.T)
    ycbcr[:, :, [1, 2]] += 128
    return np.uint8(ycbcr)


# converts the ycbcr colorspace back to rgb
def ycbcr2rgb(im):
    xform = np.array([[1, 0, 1.402], [1, -0.34414, -.71414], [1, 1.772, 0]])
    rgb = im.astype(np.float)
    rgb[:, :, [1, 2]] -= 128
    rgb = rgb.dot(xform.T)
    np.putmask(rgb, rgb > 255, 255)
    np.putmask(rgb, rgb < 0, 0)
    return np.uint8(rgb)


# padding the image
def matrix_multiple_of_eight(image):
    while (len(image) % 8) > 0:
        pad = np.zeros(len(image[0])).reshape(1, len(image[0]))
        image = np.r_[image, pad]
    while (len(image[0]) % 8) > 0:
        pad = np.zeros(len(image)).reshape(len(image), 1)
        image = np.c_[image, pad]
    return image


def calc_matrix_eight_size(image_layer):
    row_count, col_count = image_layer.shape[0], image_layer.shape[1]
    while (row_count % 8) > 0:
        row_count += 1
    while (col_count % 8) > 0:
        col_count += 1
    return row_count, col_count


# grab top row of 8 by 8 and 0:4
def capture(image_patch, c_layer=False):
    if c_layer:
        return np.round(image_patch[0,:][0:5].astype(int))
    return np.round(image_patch[0,:].astype(int))


def rebuild(image):
    return np.round(np.append(image, [0]*(64-len(image))).reshape((8, 8)))


def zig_zag(input_matrix, block_size=8, debug=False):
    if debug: print(np.round(input_matrix)); print()
    z = np.empty([block_size * block_size])
    index = -1
    for i in range(0, 2 * block_size - 1):
        if i < block_size:
            bound = 0
        else:
            bound = i - block_size + 1
        for j in range(bound, i - bound + 1):
            index += 1
            if i % 2 == 1:
                z[index] = input_matrix[j, i - j]
            else:
                z[index] = input_matrix[i - j, j]
    z = z.reshape((8, 8), order='C')
    if debug: print("zig zag: ", np.round(z)); print()
    return np.round(z)


def zig_zag_reverse(input_matrix, block_size=8, debug=False):
    input_matrix = np.squeeze(input_matrix.reshape((1, 64), order='C'))
    output_matrix = np.empty([block_size, block_size])
    index = -1
    for i in range(0, 2 * block_size - 1):
        if i < block_size:
            bound = 0
        else:
            bound = i - block_size + 1
        for j in range(bound, i - bound + 1):
            index += 1
            if i % 2 == 1:
                output_matrix[j, i - j] = input_matrix[index]
            else:
                output_matrix[i - j, j] = input_matrix[index]
    if debug: print("zig zag reverse: ", output_matrix); print()
    return output_matrix


def dct_2d(image, debug=False):
    if debug: print(image); print()
    image.astype(float)
    if debug: print("dct: ", np.round(fftpack.dct(fftpack.dct(image.T, norm='ortho').T, norm='ortho'))); print()
    return fftpack.dct(fftpack.dct(image.T, norm='ortho').T, norm='ortho')


def idct_2d(image, debug=False):
    if debug: print(image); print()
    image.astype(float)
    if debug: print("idct: ", fftpack.idct(fftpack.idct(image.T, norm='ortho').T, norm='ortho')); print()
    return fftpack.idct(fftpack.idct(image.T, norm='ortho').T, norm='ortho')


def merge_blocks(input_list, rows, columns):
    all_rows_concatenated = []
    append = all_rows_concatenated.append
    for row in range(rows):
        this_row_items = input_list[(columns * row):(columns * (row + 1))]
        append(np.concatenate(this_row_items, axis=1))
    output_matrix = np.concatenate(all_rows_concatenated, axis=0)
    return output_matrix


def quantize(input, debug=False, c_layer=False):
    if debug: print(input); print()
    q = np.array([[16, 13, 18, 15, 25, 27, 29, 31],
                  [12, 11, 11, 19, 26, 58, 60, 55],
                  [9, 14, 15, 27, 40, 57, 69, 56],
                  [11, 13, 15, 29, 51, 87, 80, 62],
                  [11, 13, 15, 56, 68, 109, 103, 77],
                  [24, 35, 55, 64, 81, 104, 113, 92],
                  [49, 64, 78, 87, 103, 121, 120, 101],
                  [72, 92, 95, 98, 112, 100, 103, 99]])
    q_c = np.array([[17, 19, 27, 47, 99, 99, 99, 99],
                    [13, 16, 26, 66, 99, 99, 99, 99],
                    [15, 26, 56, 99, 99, 99, 99, 99],
                    [47, 66, 99, 99, 99, 99, 99, 99],
                    [99, 99, 99, 99, 99, 99, 99, 99],
                    [99, 99, 99, 99, 99, 99, 99, 99],
                    [99, 99, 99, 99, 99, 99, 99, 99],
                    [99, 99, 99, 99, 99, 99, 99, 99]])
    if debug: print("quantize: ", input/q); print()
    if c_layer:
        return input / q_c
    return input / q


def undo_quantize(input, debug=False, c_layer=False):
    if debug: print(input); print()
    q = np.array([[16, 13, 18, 15, 25, 27, 29, 31],
                  [12, 11, 11, 19, 26, 58, 60, 55],
                  [9, 14, 15, 27, 40, 57, 69, 56],
                  [11, 13, 15, 29, 51, 87, 80, 62],
                  [11, 13, 15, 56, 68, 109, 103, 77],
                  [24, 35, 55, 64, 81, 104, 113, 92],
                  [49, 64, 78, 87, 103, 121, 120, 101],
                  [72, 92, 95, 98, 112, 100, 103, 99]])
    q_c = np.array([[17, 19, 27, 47, 99, 99, 99, 99],
                    [13, 16, 26, 66, 99, 99, 99, 99],
                    [15, 26, 56, 99, 99, 99, 99, 99],
                    [47, 66, 99, 99, 99, 99, 99, 99],
                    [99, 99, 99, 99, 99, 99, 99, 99],
                    [99, 99, 99, 99, 99, 99, 99, 99],
                    [99, 99, 99, 99, 99, 99, 99, 99],
                    [99, 99, 99, 99, 99, 99, 99, 99]])
    if debug: print("undo quantize: ", input*q); print()
    if c_layer:
        return input * q_c
    return input * q


# def rearrangeDC(compressed_values, layer=None):
#     if layer == 1:
#         for x in range(0, len(compressed_values), 3):
#             compressed_values.append(compressed_values.pop(x))
#         compressed_valuesAC = compressed_values[:int(len(compressed_values) * 3 / 4)]
#         compressed_valuesDC = compressed_values[int(len(compressed_values) * 3 / 4):]
#     else:
#         for x in range(0, len(compressed_values), 7):
#             compressed_values.append(compressed_values.pop(x))
#         compressed_valuesAC = compressed_values[:int(len(compressed_values) * 7 / 8)]
#         compressed_valuesDC = compressed_values[int(len(compressed_values) * 7 / 8):]
#     compressed_valuesDC.insert(0, compressed_valuesDC.pop(len(compressed_valuesDC) - 1))
#     return compressed_valuesAC, compressed_valuesDC


def writeFile(bitstring, fileName=None):
    writeable_string = StringIO(bitstring)
    f = open(fileName + '.bin', 'w')

    while 1:
        b = writeable_string.read(8)
        if not b:
            break
        if len(b) < 8:
            b = b + '0' * (8 - len(b))

        c = chr(int(b, 2))
        f.write(c)
    f.close()


def readFile():
    return


