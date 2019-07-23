from scipy.fftpack import dct, idct
import numpy as np


''' original quantization table for reference '''
ORGQUANT = np.array([[16, 11, 10, 16, 24, 40, 51, 61],
                     [12, 12, 14, 19, 26, 58, 60, 55],
                     [14, 13, 16, 24, 40, 57, 69, 56],
                     [14, 17, 22, 29, 51, 87, 80, 62],
                     [18, 22, 37, 56, 68, 109, 103, 77],
                     [24, 35, 55, 64, 81, 104, 113, 92],
                     [49, 64, 78, 87, 103, 121, 120, 101],
                     [72, 92, 95, 98, 112, 100, 103, 99]], dtype=np.float16)

QUANTIZATIONTABLE = np.array([[11,  8,  8, 11, 11, 10, 16, 10],
                              [11, 16, 13, 16, 16, 16,  7, 28],
                              [13, 13, 13, 13,  7, 22, 14, 14],
                              [8, 28, 32, 36, 32, 42, 43, 36],
                              [43, 43, 43, 40, 64, 53, 45, 54],
                              [53, 53, 39, 39, 56, 64, 64, 64],
                              [64, 75, 75, 74, 74, 43, 54, 79],
                              [80, 80, 70, 80, 60, 60, 80, 69]],  dtype=np.float16)

CHROMQUANTIZATIONTABLE = np.array([[12, 13, 13, 18, 15, 15, 21, 13],
                                   [15, 21, 57, 39, 29, 40, 57, 57],
                                   [57, 57, 57, 57, 57, 57, 57, 57],
                                   [57, 57, 69, 57, 57, 67, 70, 57],
                                   [69, 57, 57, 57, 69, 70, 70, 57],
                                   [70, 70, 69, 57, 57, 57, 70, 69],
                                   [57, 70, 57, 57, 57, 57, 57, 57],
                                   [57, 57, 57, 57, 57, 57, 57, 57]], dtype=np.float16)


def split(matrix, nrows, ncols):
    """Split a matrix into sub-matrices."""
    return np.array([np.array(matrix[x:x + nrows, y:y + ncols], dtype=np.int8) for x in range(0, matrix.shape[0], nrows)
                     for y in range(0, matrix.shape[1], ncols)], dtype=np.int8)


# converts rgb to ycbcr colorspace
def rgb2ycbcr(im):
    im.astype(np.float)
    xform = np.array([[.299, .587, .114], [-.1687, -.3313, .5], [.5, -.4187, -.0813]])
    ycbcr = im.dot(xform.T)
    ycbcr[:, :, [1, 2]] += 128
    return np.uint8(np.round(ycbcr))


# converts the ycbcr colorspace back to rgb
def ycbcr2rgb(im):
    xform = np.array([[1, 0, 1.402], [1, -0.34414, -.71414], [1, 1.772, 0]])
    rgb = im.astype(np.float)
    rgb[:, :, [1, 2]] -= 128
    rgb = rgb.dot(xform.T)
    np.putmask(rgb, rgb > 255, 255)
    np.putmask(rgb, rgb < 0, 0)
    return np.uint8(np.round(rgb))


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
def capture(image_patch, values=64, sample_percentage=1):
    image_patch = image_patch.astype(np.int16)
    if sample_percentage != 1:
        return image_patch[:int(values * sample_percentage)]
    return image_patch[:int(values)]


def rebuild(image):
    return np.append(image, [0]*(64-len(image)))


def zig_zag(input_matrix, block_size=8, debug=False):
    if debug: print(np.round(input_matrix)); print()
    z = np.empty([block_size * block_size], dtype=np.int8)
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
    if debug: print("zig zag: ", np.round(z)); print()
    return z


def zig_zag_reverse(input_matrix, block_size=8, debug=False):
    output_matrix = np.empty([block_size, block_size], dtype=np.int8)
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
    return output_matrix.astype(np.int8)


def dct_2d(image, debug=False):
    if debug: print("image patch before dct: ", image); print()
    image.astype(float)
    # if debug: print("dct: ", np.round(dct(dct(image.T, norm='ortho').T, norm='ortho'))); print()
    # return dct(dct(image.T, norm='ortho').T, norm='ortho')
    if debug: print("dct: ",  dct(dct(image, axis=0, norm='ortho'), axis=1, norm='ortho'))
    return dct(dct(image, axis=0, norm='ortho'), axis=1, norm='ortho')


def idct_2d(image, debug=False):
    if debug: print("image patch before idct: ", image); print()
    # if debug: print("idct: ", np.round(idct(idct(image.T, norm='ortho').T, norm='ortho'))); print()
    # inversed = np.round(idct(idct(image.T, norm='ortho').T, norm='ortho'))
    if debug: print("idct: ", idct(idct(image, axis=0, norm='ortho'), axis=1, norm='ortho'))
    inversed = np.round(idct(idct(image, axis=0, norm='ortho'), axis=1, norm='ortho'))
    inversed[inversed > 127] = 127; inversed[inversed < -128] = -128
    return inversed


def merge_blocks(input_list, rows, columns):
    all_rows_concatenated = []
    append = all_rows_concatenated.append
    for row in range(rows):
        this_row_items = input_list[(columns * row):(columns * (row + 1))]
        append(np.concatenate(this_row_items, axis=1))
    output_matrix = np.concatenate(all_rows_concatenated, axis=0)
    return output_matrix


def quantize(quant, table=ORGQUANT, debug=False):
    if debug:
        print("patch before quantization: ", np.round(quant)); print();
        print("quantize: ", (quant / table).astype(np.int16)); print()
    quantized = np.round(quant / table)
    quantized[quantized > 127] = 127; quantized[quantized < -128] = -128
    return quantized.astype(np.int8)


def undo_quantize(quant, table=ORGQUANT, debug=False):
    if debug:
        print("patch before undo quantize: ", quant); print()
        print("undo quantize: ", quant.astype(np.float16) * table); print()
    return quant.astype(float) * table


