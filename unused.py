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