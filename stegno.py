#lsb steganography

def get_valid_choice(ask, allowed):  # function to force valid user input
    while True:  # loop until correct input
        x = input(ask).strip().lower()  # read user input
        if x in allowed:  # check if input is allowed
            return x  
        print("wrong choice try again")  


class stegobmp:  
    def __init__(self, file_path1):  
        self.file_path1 = file_path1  # store bmp path
        self.data = None  # placeholder for bmp data
        self.width = 0  # image width
        self.height = 0  # image height
        self.pix_start = 0  # pixel data start offset
        self.totalpix1 = 0  # total number of pixels
        self._load_bmp()  

    def _load_bmp(self):  # internal bmp loading function
        try:
            f = open(self.file_path1, "rb")  # try opening bmp
        except FileNotFoundError:
            print("file not found")  
            return  # stop loading

        self.data = bytearray(f.read())  # read bmp bytes
        f.close()  # close file

        if len(self.data) < 54:  # check bmp header size
            print("invalid bmp")  # header too small
            self.data = None  # invalidate data
            return  

        self.pix_start = int.from_bytes(self.data[10:14], "little")  # pixel offset
        self.width = int.from_bytes(self.data[18:22], "little")  # read width
        self.height = int.from_bytes(self.data[22:26], "little")  # read height
        bpp = int.from_bytes(self.data[28:30], "little")  # bits per pixel

        if bpp != 24:  # only allow 24 bit bmp
            print("not 24 bit bmp")  # unsupported format
            self.data = None  # invalidate
            return 

        if self.height < 0:  # check for top down bmp
            print("unsupported bmp type")  
            self.data = None  # invalidate
            return  

        row_size = ((24 * self.width + 31) // 32) * 4  # bmp row size formula
        if row_size != self.width * 3:  # check padding
            print("bmp has extra row bytes")  # padding not supported
            self.data = None  # invalidate
            return  

        self.totalpix1 = self.width * self.height  # calculate total pixels

    def can_fit_bits(self, bits):  # check if message fits image
        return len(bits) <= self.totalpix1 * 3  # 3 bits per pixel

    def insert_bits(self, bits):  # insert bits into bmp pixels
        bit_index = 0  # index for bits
        pix_index = 0  # index for pixels

        while bit_index < len(bits) and pix_index < self.totalpix1:  # smart looping
            pos = self.pix_start + pix_index * 3  # pixel byte position
            for c in range(3):  # loop through r g b
                if bit_index >= len(bits):  # stop when done
                    break  # exit loop
                self.data[pos + c] = (self.data[pos + c] & 0b11111110) | bits[bit_index]  # set lsb
                bit_index += 1  # move to next bit
            pix_index += 1  # move to next pixel

    def extract_lsbs(self):  # extract all lsb bits
        decoded_bits = []  # list for extracted bits
        for p in range(self.totalpix1):  # loop pixels
            pos = self.pix_start + p * 3  # pixel position
            decoded_bits.append(self.data[pos] & 1)  # blue lsb
            decoded_bits.append(self.data[pos + 1] & 1)  # green lsb
            decoded_bits.append(self.data[pos + 2] & 1)  # red lsb
        return decoded_bits  # return bits


def encode_flow():  # encoding process
    input_file1 = input("input bmp ").strip()  # ask for bmp file
    stego = stegobmp(input_file1)  # create bmp object

    if stego.data is None:  # check if bmp failed
        return  

    option = get_valid_choice("secret text t or file f ", ["t", "f"])  # dual input

    if option == "t":  # text input mode
        inp = input("enter secret text ")  
        if inp == "":  # empty message check
            print("empty message")  
            return  
        encoded1 = inp.encode("utf-8")  # convert to bytes
    else:  # file input mode
        sec = input("secret file ").strip()  
        try:
            f = open(sec, "rb")  # open file
            encoded1 = f.read()  # read bytes
            f.close()  # close file
        except FileNotFoundError:
            print("secret file missing")  
            return  
        if len(encoded1) == 0:  # empty file check
            print("file empty")  
            return  

    header = len(encoded1).to_bytes(4, "big")  # 4 byte length header
    payload = header + encoded1  # combine header and data

    bits = []  # list for message bits
    for b in payload:  # loop bytes
        for bit_pos in range(7, -1, -1):  # msb to lsb
            bits.append((b >> bit_pos) & 1)  # extract bit

    if not stego.can_fit_bits(bits):  # capacity check
        print("message too big")  
        return  

    stego.insert_bits(bits)  # embed bits

    save_as = input("output bmp ").strip()  
    if save_as == "":  # empty output name
        print("no output name")  
        return  

    try:
        out = open(save_as, "wb")  # open output bmp
        out.write(stego.data)  # write data
        out.close()  # close file
        print("saved", save_as)  
    except:
        print("save failed")  


def decode_flow():  # decoding process
    input_file1 = input("stego bmp ").strip()  # ask stego image
    stego = stegobmp(input_file1)  # load bmp

    if stego.data is None:  # invalid bmp
        return  

    bits = stego.extract_lsbs()  # extract all bits

    if len(bits) < 32:  # header existence check
        print("no message found")  
        return  

    message_len = 0  # message length variable
    for i in range(32):  # read header bits
        message_len = (message_len << 1) | bits[i]  # rebuild length

    bits_needed = message_len * 8  # calculate needed bits

    if len(bits) < 32 + bits_needed:  # corruption check
        print("message incomplete")  
        return  

    message_bits = bits[32:32 + bits_needed]  # extract message bits

    msg_bytes = []  # list for bytes
    cur = 0  # current byte
    count = 0  # bit counter
    for bit in message_bits:  # loop bits
        cur = (cur << 1) | bit  # build byte
        count += 1  # increment count
        if count == 8:  # byte complete
            msg_bytes.append(cur)  # store byte
            cur = 0  # reset
            count = 0  # reset

    option = get_valid_choice("show text t or save f ", ["t", "f"])  

    if option == "t":  # print text
        try:
            print(bytearray(msg_bytes).decode("utf-8"))  # try decode
        except:
            print("binary data cannot display")  
    else:  # save to file
        save_file = input("output file ").strip()  # ask file name
        if save_file == "":  # empty name check
            print("no output name")  
            return  
        try:
            w = open(save_file, "wb")  # open file
            w.write(bytearray(msg_bytes))  # write data
            w.close()  # close file
            print("saved", save_file)  
        except:
            print("save error") 


def main():  # main menu
    option = get_valid_choice("encode e or decode d ", ["e", "d"])  
    if option == "e":  # encode mode
        encode_flow()  # call encode
    else:  # decode mode
        decode_flow()  # call decode

main() 