import numpy as np

import lz4.frame as lz
import lzma
import bz2

import struct


def bz2_c(compressed, output_file, write=False):
    def bz2_comp(output, output_file):
        filename = output_file + ".bz2"
        with bz2.open(filename, "wb") as f:
            output = bz2.compress(output, 9)
            if write:
                f.write(output)
        return len(output)
    compressed = (struct.pack('B' * len(compressed), *compressed))
    size = bz2_comp(compressed, output_file)
    return size


def bz2_u(file_name):
    def bz2_decomp(file):
        with bz2.open(file, "rb") as f:
            f_content = f.read()
            f_content = bz2.decompress(f_content)
        return f_content
    result_bytes = bz2_decomp(file_name + '.bz2')
    fmt = "%db" % len(result_bytes)
    result_bytes = np.asarray(list(struct.unpack(fmt, result_bytes)))
    return result_bytes


def lz4compressor(values):
    with lz.LZ4FrameCompressor() as compressor:
        compressed = compressor.begin()
        compressed += compressor.compress(bytes(values))
        compressed += compressor.flush()
    return compressed


def lz4decompressor(values):
    with lz.LZ4FrameDecompressor() as decompressor:
        decompressed = decompressor.decompress(values)
    return decompressed


def bz2compressor(values):
    return list(bz2.compress(bytes(values), 9))


def bz2decompressor(values):
    return list(bz2.decompress(bytes(values)))


def lzmacompressor(values):
    return list(lzma.compress(bytes(values)))


def lzmadecomressor(values):
    return list(lzma.decompress(bytes(values)))
