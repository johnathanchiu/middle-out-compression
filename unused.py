""" This file contains unused methods that may be helpful for the future """
from middleOut.MiddleOut import MiddleOutUtils
from middleOut.MiddleOut import MiddleOut

def rearrangeDC(compressed_values, layer=None):
    if layer == 1:
        for x in range(0, len(compressed_values), 3):
            compressed_values.append(compressed_values.pop(x))
        compressed_valuesAC = compressed_values[:int(len(compressed_values) * 3 / 4)]
        compressed_valuesDC = compressed_values[int(len(compressed_values) * 3 / 4):]
    else:
        for x in range(0, len(compressed_values), 7):
            compressed_values.append(compressed_values.pop(x))
        compressed_valuesAC = compressed_values[:int(len(compressed_values) * 7 / 8)]
        compressed_valuesDC = compressed_values[int(len(compressed_values) * 7 / 8):]
    compressed_valuesDC.insert(0, compressed_valuesDC.pop(len(compressed_valuesDC) - 1))
    return compressed_valuesAC, compressed_valuesDC


def unaryconverter(lis):
    unary = []
    for y in lis:
        [unary.append('1') for _ in range(y)]
        unary.append('0')
    return ''.join(unary)


@staticmethod
def build_library2(uncompressed, size=8):
    dictionary = {}
    for part in uncompressed:
        len_of_x = len(part)
        if len_of_x >= size:
            for y in range(len_of_x - size + 1):
                par = part[y:y+size]
                if par not in dictionary:
                    dictionary[par] = 1
                else:
                    dictionary[par] += 1
    largest = MiddleOutUtils.keywithmaxval(dictionary)
    print(largest)
    print(dictionary[largest])
    return largest

@staticmethod
def eight_bit_compression2(uncompressed, lib):
    compressed, unc = [], []
    compression_lib = MiddleOut.build_dict(lib, sets=1)
    for partition in uncompressed:
        partition += ' '
        count = 0
        temp = ''
        while count < len(partition) - 1:
            compressor = 6
            mo = partition[count:count + compressor]
            while mo in compression_lib:
                compressor += 1
                mo = partition[count:count + compressor]
            mo = mo[:-1]
            length_string = len(mo)
            if length_string >= 6:
                if temp != '':
                    unc.append(temp)
                    temp = ''
                compressed.append(compression_lib[mo])
                count += length_string
            else:
                temp += partition[count]
                count += 1
        if temp != '':
            unc.append(temp)
    return compressed, unc

@staticmethod
def getliteral(lis):
    len_of_lis = len(lis)
    if len_of_lis <= 2:
        return MiddleOutUtils.get_literal_small(lis)
    elif len_of_lis <= 6:
        return MiddleOutUtils.get_literal(lis)
    elif len_of_lis <= 22:
        return MiddleOutUtils.get_literal_long(lis)
    elif len_of_lis <= 86:
        return MiddleOutUtils.get_literal_large(lis)
    return MiddleOutUtils.get_literal_large(lis[:86]) + MiddleOut.getliteral(lis[86:])

@staticmethod
def merge_compression(layer_one, layer_two):
    count = 0
    for x in range(len(layer_one)):
        if layer_one[x] == 0:
            layer_one[x] = layer_two[count]
            count += 1
    return ''.join(layer_one)

@staticmethod
def get_literal_long(stream):
    return '101' + MiddleOutUtils.convertBin(len(stream) - 7, bits=4) + stream

@staticmethod
def get_literal(stream):
    return '100' + MiddleOutUtils.convertBin(len(stream) - 3, bits=2) + stream

@staticmethod
def get_literal_small(stream):
    return '00' + MiddleOutUtils.convertBin(len(stream) - 1, bits=1) + stream

@staticmethod
def get_literal_large(stream):
    return '111110' + MiddleOutUtils.convertBin(len(stream) - 23, bits=6) + stream