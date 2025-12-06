def read_bmp(path):
    #try opening the file
    try:
        f = open(path, "rb")
    except FileNotFoundError:
        print("file not found")
        return None, None, None, None

    data = bytearray(f.read())
    f.close()

    #bmp header check
    if len(data) < 54:
        print("invalid bmp file")
        return None, None, None, None

    #read important header fields
    pix_start = int.from_bytes(data[10:14], "little")
    width = int.from_bytes(data[18:22], "little")
    height = int.from_bytes(data[22:26], "little")
    bpp = int.from_bytes(data[28:30], "little")

    #24 bit bmp files
    if bpp != 24:
        print("not a 24bit bmp")
        return None, None, None, None

    return data, width, height, pix_start


def bytes_to_bits(b):
    # converts bytes into a list of bits
    bits = []
    for x in b:
        for i in range(7, -1, -1):
            bits.append((x >> i) & 1)
    return bits


def bits_to_bytes(bits):
    # convert bits back into bytes
    out = []
    cur = 0
    count = 0
    for bit in bits:
        cur = (cur << 1) | bit
        count += 1
        if count == 8:
            out.append(cur)
            cur = 0
            count = 0
    return out


def encode():
    # to do
    print("")


def decode():
    # to do
    print("")


def main():
    mode = input("encode (e) or decode (d)? ").strip().lower()

    if mode == "e":
        encode()
    else:
        decode()


main()
