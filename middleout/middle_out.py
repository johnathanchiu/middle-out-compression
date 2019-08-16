# Middle-Out Compression Algorithm
# © Johnathan Chiu, 2019

from middleout.run_length import *
from middleout.utils import *

from multiprocessing import Pool
from tqdm import tqdm


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
        literal_count, pointer, match_start = 0, 0, 0
        while pointer < len(uncompressed):
            match = uncompressed[pointer:pointer+2]
            match_start = pointer

            if MiddleOut.DEBUG:
                print("pointer:", pointer, "match:", match)
                print("match start:", match_start)
                print("compressed:", compressed_stream)
                frmt = "{:>3}"*len(uncompressed)
                print(frmt.format(*list(range(0, len(uncompressed)))))
                print(frmt.format(*uncompressed))

            while tuple(match) in preceding and match_start - len(match) >= preceding[tuple(match)]:
                if len(match) == 2:
                    pointer += 1
                pointer += 1
                if pointer >= len(uncompressed):
                    back_reference = unsigned_binary(preceding[tuple(match)], bits=MiddleOut.BIT_DEPTH)
                    reference_size = unsigned_binary(len(match) - 2, bits=MiddleOut.DISTANCE_ENCODER)
                    compressed_stream += '0' + back_reference + reference_size; match = []
                    break
                match.append(uncompressed[pointer])

            if len(match) > 2:
                hanging, match = match[-1:], match[:-1]
                back_reference = unsigned_binary(preceding[tuple(match)], bits=MiddleOut.BIT_DEPTH)
                reference_size = unsigned_binary(len(match) - 2, bits=MiddleOut.DISTANCE_ENCODER)
                compressed_stream += '0' + back_reference + reference_size
                pointer -= 1

            else:
                if len(match) >= 1:
                    literal_count += 1
                    compressed_stream += '1'; right.append(match[0])

            if pointer <= len(uncompressed) - MiddleOut.MAX_DISTANCE:
                forward_values = uncompressed[pointer:pointer+MiddleOut.MAX_DISTANCE]
                for j in range(2, len(forward_values) + 1):
                    if tuple(forward_values[:j]) not in preceding:
                        preceding[tuple(forward_values[:j])] = pointer
            pointer += 1
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
        if length == 0: return [], ''
        iden, compressed = compressed[0], compressed[1:]

        if iden == '1':
            return unsigned_int_list(compressed[:length*8]), compressed[length*8:]
        partition, remaining, back_trans_count = MiddleOutUtils.partition_compressed_bits(compressed, length)
        right, compressed = MiddleOutDecompressor.bit_decompress(remaining, back_trans_count)
        total = MiddleOutDecompressor.merge_bytes(partition, right)
        return total, compressed


class MiddleOut:
    """ Passes values into the compressor and decompressor, pads streams """

    BIT_DEPTH, STRIDE = 8, 256
    DISTANCE_ENCODER, MAX_DISTANCE = 3, 9
    DEBUG = False

    @staticmethod
    def middle_out_compress(partitions):
        with Pool(8) as p:
            compression = p.map(MiddleOutCompressor.byte_compression, partitions)
        return ''.join(compression)

    @staticmethod
    def middle_out_decompress(bit_stream, bytes_count, visualizer=True):
        byte_chunks = []
        partitions, remainder = bytes_count // MiddleOut.STRIDE, bytes_count % MiddleOut.STRIDE
        if visualizer:
            parts = tqdm(range(partitions + 1), desc='running middle-out decompression scheme')
        else:
            parts = range(partitions + 1)
        for c in parts:
            if c == partitions:
                decompressed, bit_stream = MiddleOutDecompressor.bit_decompress(bit_stream, remainder)
                byte_chunks.append(decompressed)
            else:
                decompressed, bit_stream = MiddleOutDecompressor.bit_decompress(bit_stream, MiddleOut.STRIDE)
                byte_chunks.append(decompressed)
        return (lambda l: [item for sublist in l for item in sublist])(byte_chunks)

    @staticmethod
    def compress(byte_stream, stride=256, distance=9, visualizer=True):
        assert stride >= 256 and stride % 256 == 0, "invalid back reference size"
        try:
            assert (2 ** minimum_bits(distance - 2)) - 1 == distance - 2
        except AssertionError:
            dist = distance
            while (2 ** minimum_bits(dist)) - 1 > distance - 2:
                distance += 1

        partitions = split_file(byte_stream, chunksize=stride)

        if visualizer:
            parts = tqdm(partitions, desc='running middle-out compression scheme')
        else:
            parts = partitions

        MiddleOut.DISTANCE_ENCODER, MiddleOut.STRIDE = minimum_bits(distance - 2), stride
        MiddleOut.BIT_DEPTH, MiddleOut.MAX_DISTANCE = minimum_bits(stride - 1), distance

        mo, minbits = MiddleOut.middle_out_compress(parts), minimum_bits(len(byte_stream))

        stride_bits, distance_bits = unaryconverter(stride // 256), unsigned_binary(distance)
        header = unaryconverter(minbits) + unsigned_binary(len(byte_stream), bits=minbits) + stride_bits + distance_bits

        compressed = header + mo; pad = pad_stream(len(compressed)); num_padded = signed_bin(pad, bits=4)
        mo_compressed = compressed + ('0' * pad) + num_padded

        return unsigned_int_list(mo_compressed)

    @staticmethod
    def decompress(compressed_bits, visualizer=True):

        compressed_bits = remove_padding(compressed_bits)

        bit_count_length = unary_to_int(compressed_bits)
        compressed_bits = compressed_bits[bit_count_length+1:]
        length, compressed_bits = unsigned_int(compressed_bits[:bit_count_length]), compressed_bits[bit_count_length:]
        stride_size = unary_to_int(compressed_bits) * 256; compressed_bits = compressed_bits[int(stride_size//256)+1:]
        distance, compressed_bits = unsigned_int(compressed_bits[:8]), compressed_bits[8:]

        MiddleOut.DISTANCE_ENCODER, MiddleOut.STRIDE = minimum_bits(distance - 2), stride_size
        MiddleOut.BIT_DEPTH, MiddleOut.MAX_DISTANCE = minimum_bits(stride_size - 1), distance

        return MiddleOut.middle_out_decompress(compressed_bits, length, visualizer=visualizer)
