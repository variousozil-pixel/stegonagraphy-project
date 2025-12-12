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
    # load input image
    bmp = input("enter bmp file: ").strip()
    data, w, h, pix_start = read_bmp(bmp)

    if data is None:
        print("wrong file or not 24-bit bmp")
        return

    # choose text or file for secret
    mode = input("text (t) or file (f)? ").strip().lower()

    if mode == "t":
        secret = input("enter message: ")
        msg = secret.encode("utf-8")

    elif mode == "f":
        fname = input("enter secret file: ").strip()
        try:
            f = open(fname, "rb")
            msg = f.read()
            f.close()
        except:
            print("file not found")
            return
    else:
        print("wrong choice")
        return

    if len(msg) == 0:
        print("empty message")
        return

    # make 4-byte length header
    header = len(msg).to_bytes(4, "big")
    payload = header + msg

    # convert payload to bits
    bits = []
    for b in payload:
        for i in range(7, -1, -1):
            bits.append((b >> i) & 1)

    # check if it fits
    total_pixels = w * h
    max_bits = total_pixels * 3

    if len(bits) > max_bits:
        print("message too big for image")
        return

    # embed bits
    bit_i = 0
    pixel_i = 0

    while bit_i < len(bits) and pixel_i < total_pixels:
        pos = pix_start + pixel_i * 3
        for c in range(3):
            if bit_i >= len(bits):
                break
            data[pos + c] = (data[pos + c] & 0xFE) | bits[bit_i]
            bit_i += 1
        pixel_i += 1

    # save
    outname = input("output bmp name: ").strip()
    try:
        f = open(outname, "wb")
        f.write(data)
        f.close()
        print("saved as", outname)
    except:
        print("could not save")


def decode():
    # load bmp
    bmp = input("enter bmp file: ").strip()
    data, w, h, pix_start = read_bmp(bmp)

    if data is None:
        print("wrong file or not 24 bit bmp")
        return

    # extract lsb bits
    bits = []
    total_pixels = w * h

    for i in range(total_pixels):
        pos = pix_start + i * 3
        # get the lsb from R, G , B
        bits.append(data[pos] & 1)
        bits.append(data[pos + 1] & 1)
        bits.append(data[pos + 2] & 1)

    # need at least 32 bits for header
    if len(bits) < 32:
        print("no hidden message or corrupted data")
        return

    # read 4-byte length header
    msg_len = 0
    for i in range(32):
        msg_len = (msg_len << 1) | bits[i]

    #extract the message bits
    needed_bits = msg_len * 8

    if len(bits) < 32 + needed_bits:
        print("not enough data to extract full message")
        return

    msg_bits = bits[32 : 32 + needed_bits]

    # convert bits back to bytes
    msg_bytes = []
    cur = 0
    bit_count = 0

    for b in msg_bits:
        cur = (cur << 1) | b
        bit_count += 1
        if bit_count == 8:
            msg_bytes.append(cur)
            cur = 0
            bit_count = 0

    # ask user how to output
    choice = input("print text (t) or save to file (f)? ").strip().lower()

    if choice == "t":
        # try utf-8 decode
        try:
            text = bytearray(msg_bytes).decode("utf-8")
            print("decoded message:")
            print(text)
        except:
            print("message is not utf-8 text")
            print(msg_bytes)
    else:
        out_name = input("output file name: ").strip()
        try:
            with open(out_name, "wb") as f:
                f.write(bytearray(msg_bytes))
            print("saved to", out_name)
        except:
            print("could not save file")


def main():
    mode = input("encode (e) or decode (d)? ").strip().lower()

    if mode == "e":
        encode()
    else:
        decode()


main()
