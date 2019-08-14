# Middle-Out Compression Algorithm
# © Johnathan Chiu, 2019

from middleout.runlength import rld, rle, rlepredict
from middleout.utils import *

from multiprocessing import Pool


class MiddleOutUtils:
    """ Utils Class for MiddleOut """

    @staticmethod
    def partition_compressed_bits(bit_stream, size):
        pointer = 0
        back_transform, total = 0, 0
        dist, max_bits = MiddleOut.DISTANCE_ENCODER, MiddleOut.BIT_DEPTH

        while total < size:
            if bit_stream[pointer] == '1':
                total += 1; back_transform += 1; pointer += 1
            else:
                pointer += 1
                start, end = pointer + max_bits, pointer + max_bits + dist
                total += unsigned_int(bit_stream[start:end]) + 2
                pointer += dist + max_bits

        return bit_stream[:pointer], bit_stream[pointer:], back_transform


class MiddleOutCompressor:
    """ Compressor Class """

    @staticmethod
    def byte_compression(uncompressed):
        compressed_stream = ''
        preceding, match, right = {}, [], []
        position, match_start, literal_count = 0, 0, 0
        for i in range(0, len(uncompressed) + 1):
            if i < len(uncompressed): match.append(uncompressed[i])
            match_iden = tuple(match)
            if match_iden in preceding:
                if preceding[match_iden] + MiddleOut.MAX_DISTANCE <= match_start:
                    if i == len(uncompressed):
                        match_pos = unsigned_binary(preceding[match_iden])
                        match_length = unsigned_binary(len(match_iden) - 2, bits=MiddleOut.DISTANCE_ENCODER)
                        compressed_stream += '0' + match_pos + match_length
                        match = []
                    else:
                        if len(match_iden) == MiddleOut.MAX_DISTANCE:
                            match_pos = unsigned_binary(preceding[match_iden], bits=MiddleOut.BIT_DEPTH)
                            match_length = unsigned_binary(MiddleOut.MAX_DISTANCE - 2, bits=MiddleOut.DISTANCE_ENCODER)
                            compressed_stream += '0' + match_pos + match_length
                            match, match_start = [], i + 1
                else:
                    literal_count += len(match_iden); compressed_stream += '1' * len(match_iden)
                    [right.append(c) for c in match]; match, match_start = [], i + 1
            else:
                if i == len(uncompressed):
                    compressed_stream += '1' * len(match); [right.append(c) for c in match]; match = []
                else:
                    if len(match_iden) == 2:
                        literal_count += len(match_iden)
                        compressed_stream += '1' * len(match_iden)
                        [right.append(c) for c in match]
                        match, match_start = [], i + 1
                    else:
                        hanging, match_iden = match[-1], tuple(match[:-1])
                        if match_iden in preceding:
                            match_pos = unsigned_binary(preceding[match_iden])
                            match_length = unsigned_binary(len(match_iden) - 2, bits=MiddleOut.DISTANCE_ENCODER)
                            compressed_stream += '0' + match_pos + match_length
                            match, match_start = [hanging], i
            if i <= len(uncompressed) - MiddleOut.MAX_DISTANCE:
                forward_values = uncompressed[position:position+MiddleOut.MAX_DISTANCE]
                for j in range(2, len(forward_values) + 1):
                    if tuple(forward_values[:j]) not in preceding:
                        preceding[tuple(forward_values[:j])] = position
                position += 1
        if literal_count > len(uncompressed) * 0.90:
            return '1' + unsigned_bin_list(uncompressed)
        return '0' + compressed_stream + MiddleOutCompressor.byte_compression(right)


class MiddleOutDecompressor:
    """ Decompressor Class """

    @staticmethod
    def merge_bytes(compressed, right):
        bit_depth, distance_encoder = MiddleOut.BIT_DEPTH, MiddleOut.DISTANCE_ENCODER
        decompress, pointer, right_pos = [], 0, 0
        while pointer < len(compressed):
            if compressed[pointer] == '1':
                decompress.append(right[right_pos])
                right_pos += 1; pointer += 1
            else:
                back_reference = unsigned_int(compressed[pointer+1:pointer+bit_depth+1])
                copy_length = unsigned_int(compressed[pointer+bit_depth+1:pointer+bit_depth+distance_encoder+1]) + 2
                decompress += decompress[back_reference:back_reference+copy_length]
                pointer += 1 + bit_depth + distance_encoder
        return decompress

    @staticmethod
    def bit_decompress(compressed, length):
        iden, compressed = compressed[0], compressed[1:]
        if iden == '1':
            return unsigned_int_list(compressed[:length*8]), compressed[length*8:]
        partition, remaining, back_trans_count = MiddleOutUtils.partition_compressed_bits(compressed, length)
        right, compressed = MiddleOutDecompressor.bit_decompress(remaining, back_trans_count)
        return MiddleOutDecompressor.merge_bytes(partition, right), compressed


class MiddleOut:
    """ Passes values into the compressor and decompressor, pads streams """

    BIT_DEPTH, STRIDE = 8, 256
    DISTANCE_ENCODER, MAX_DISTANCE = 3, 9

    @staticmethod
    def middle_out_compress(partitions):
        with Pool(8) as p:
            compression = p.map(MiddleOutCompressor.byte_compression, partitions)
        return compression

    @staticmethod
    def middle_out_decompress(bit_stream, bytes_count):
        byte_chunks = []
        partitions, remainder = bytes_count // MiddleOut.STRIDE, bytes_count % MiddleOut.STRIDE
        for c in range(partitions + 1):
            if c == partitions:
                decompressed, bit_stream = MiddleOutDecompressor.bit_decompress(bit_stream, remainder)
                byte_chunks.append(decompressed)
            else:
                decompressed, bit_stream = MiddleOutDecompressor.bit_decompress(bit_stream, MiddleOut.STRIDE)
                byte_chunks.append(decompressed)
        return (lambda l: [item for sublist in l for item in sublist])(byte_chunks)

    @staticmethod
    def compress(byte_stream, stride=256, distance=9):
        assert stride >= 256 and stride % 256 == 0, print("invalid back reference size")

        partitions = split_file(byte_stream, chunksize=stride)

        MiddleOut.DISTANCE_ENCODER, MiddleOut.STRIDE = minimum_bits(distance - 2), stride
        MiddleOut.BIT_DEPTH, MiddleOut.MAX_DISTANCE = minimum_bits(stride - 1), distance

        mo, minbits = MiddleOut.middle_out_compress(partitions), minimum_bits(len(byte_stream))

        stride_bits, distance_bits = unaryconverter(stride // 256), unsigned_binary(distance)
        header = unaryconverter(minbits) + unsigned_binary(len(byte_stream), bits=minbits) + stride_bits + distance_bits

        compressed = header + ''.join(mo); pad = pad_stream(len(compressed)); num_padded = signed_bin(pad, bits=4)
        mo_compressed = compressed + ('0' * pad) + num_padded

        return convert_to_list(mo_compressed)

    @staticmethod
    def decompress(compressed_bits):
        compressed_bits = remove_padding(compressed_bits)

        bit_count_length = unary_to_int(compressed_bits)
        compressed_bits = compressed_bits[bit_count_length+1:]
        length, compressed_bits = unsigned_int(compressed_bits[:bit_count_length]), compressed_bits[bit_count_length:]
        stride_size = unary_to_int(compressed_bits) * 256; compressed_bits = compressed_bits[int(stride_size//256)+1:]
        distance, compressed_bits = unsigned_int(compressed_bits[:8]), compressed_bits[8:]

        MiddleOut.DISTANCE_ENCODER, MiddleOut.STRIDE = minimum_bits(distance - 2), stride_size
        MiddleOut.BIT_DEPTH, MiddleOut.MAX_DISTANCE = minimum_bits(stride_size - 1), distance

        return MiddleOut.middle_out_decompress(compressed_bits, length)







