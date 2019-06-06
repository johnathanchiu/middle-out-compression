from io import StringIO
import math


def positive_binary(num, bits=8):
    length = '{0:0' + str(bits) + 'b}'
    return length.format(num)


def positive_int(binary):
    return int(binary, 2)


def convertBin(num, bits=8):
    s = bin(num & int("1" * bits, 2))[2:]
    return ("{0:0>%s}" % (bits)).format(s)


def convertInt(binary, bits=8):
    binary = int(binary, 2)
    """compute the 2's complement of int value val"""
    if (binary & (1 << (bits - 1))) != 0:  # if sign bit is set e.g., 8bit: 128-255
        binary = binary - (1 << bits)  # compute negative value
    return binary  # return positive value as is


def convertBin_list(intList, bits=8):
    def bindigits(val, bits=8):
        s = bin(val & int("1" * bits, 2))[2:]
        return ("{0:0>%s}" % (bits)).format(s)
    binary = ''
    for x in intList:
        binary += bindigits(x, bits=bits)
    return binary


def convertInt_list(binary, bits=8):
    def two_complement(binary, bits=8):
        binary = int(binary, 2)
        """compute the 2's complement of int value val"""
        if (binary & (1 << (bits - 1))) != 0:  # if sign bit is set e.g., 8bit: 128-255
            binary = binary - (1 << bits)  # compute negative value
        return binary  # return positive value as is
    intList = []
    for x in range(0, len(binary), bits):
        intList.append(two_complement(binary[x:x+bits], bits=bits))
    return intList


def unaryconverter(num):
    unary = ''
    for _ in range(num):
        unary += '1'
    unary += '0'
    return unary


def unaryToInt(unr):
    count, num = 0, 0
    while unr[count] != '0':
        num += 1
    return num


def minimum_bits(num):
    if num == 0:
        return 1
    return num.bit_length()


# TODO: Write binary data to files
# def writeFile(bitstring, fileName=None):
#     writeable_string = StringIO(bitstring)
#     f = open(fileName + '.bin', 'w')
#     while 1:
#         b = writeable_string.read(8)
#         if not b:
#             break
#         if len(b) < 8:
#             b = b + '0' * (8 - len(b))
#
#         c = chr(int(b, 2))
#         f.write(c)
#     f.close()


# def readFile():
#     return