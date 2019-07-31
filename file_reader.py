from middleout.utils import readFileBytes

FILE_NAME = '/Users/johnathanchiu/Documents/jpeg-research/CompressionPics/tests/IMG_3692.jpg'
file_bytes = readFileBytes(FILE_NAME)

print(len(file_bytes))
for i in range(0, len(file_bytes), 1000):
    print(file_bytes[i:i+1000])
