# Middle-Out-Compression

Middleout Compression is a novel compression algorithm that presents a proof of concept to increase compression ratios for LZ77 based compressors.

This algorithm uses top-down and left-right compression simultaneously.

# Stacking Compression Algorithms

Middleout is stacked upon lz4 to give higher compression ratios.

# Usage

*__For compress.py example usage:__*

*python compress.py* [*-o* | File path to file that needs to be compressed] [*-c* | Path to folder for compressed file/default=working directory]

*__For decompress.py example usage:__*

*python decompress.py* [*-c* | File path to the compressed .bin file] [*-p* | Path to folder for decompressed file/default=working directory]

# Compression Explained

Middle-Out algorithm uses prefix codes to define literals and compressed data. Additionally, uncompressed literals are pushed to the right to be compressed again. This process is recursive and extremely fast.

# Dependencies

To be updated soon...

# Additional

__*DISCLAIMER: All rights and intellectual property to and for the algorithm belongs to the original creator of the algorithm (Johnathan Chiu). Any attempts to use this algorithm in a for-profit manner without the permission of the original creator is strictly prohibited.*__
