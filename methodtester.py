from middleOut.MiddleOut import *

import collections

x = '0000100111110000000011001111111011111010000000010000000111111000000110100000010000001000111110001111111111111111' \
    # '11111110000000010000111100001001000000'
# x = '000000000101001001011000100101010010001110000011111111110000000000'
# '000000000 10100100 101100010010 10100100 011100000 1111111111 0000000000'
layer_one, uncomp_part = MiddleOut.zero_one_filter(x)
print("layer one", layer_one)
print(uncomp_part)
lib = MiddleOut.build_library(uncomp_part)
print(lib)
layer_two, unc = MiddleOut.eight_bit_compression(uncomp_part, lib)
print("layer2", layer_two)
print("uncompressed", unc)
lib2 = MiddleOut.build_library(unc, size=4)
print(lib2)
layer_three = MiddleOut.four_bit_compression(unc, lib2)
print("layer3", layer_three)
y = MiddleOut.merge_compression(layer_one, layer_two, layer_three)
print("y", y)
lib += lib2 + y
y = lib
print("asdf", y)
z = MiddleOut.decompressStream(y)
print(z)
print(x)
print(z == x)
