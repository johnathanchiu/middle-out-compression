# Middle-Out-Compression

(Honestly was trying stuff back then and experimenting, this was just some engineering/research experimentation)

This implementation is a proof of concept to attempt to increase compression ratios.

This algorithm uses top-down and left-right compression simultaneously and runs similar to LZ algorithms.

# Stacking Compression Algorithms

Middleout is stacked upon lz4 to give higher compression ratios.

# Usage

*__For compress.py example usage:__*

*python compress.py* [*-o* | File path to file that needs to be compressed] [*-c* | Path to folder for compressed file/default=working directory]

*__For decompress.py example usage:__*

*python decompress.py* [*-c* | File path to the compressed .bin file] [*-p* | Path to folder for decompressed file/default=working directory]

# Compression Explained

This algorithm uses prefix codes to build a dictionary defining previously seen literals to compress data. Additionally, uncompressed literals are pushed to the right to be compressed again. This process is recursive and extremely fast.

# Dependencies

To be updated soon...
