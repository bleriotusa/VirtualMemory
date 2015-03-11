__author__ = 'Michael'

FRAMESIZE = 512
TOTALFRAMES = 1024


def accepts(*types):
    def check_accepts(f):
        assert len(types) == f.func_code.co_argcount

        def new_f(*args, **kwds):
            for (a, t) in zip(args, types):
                assert isinstance(a, t), \
                    "arg %r does not match %s" % (a, t)
            return f(*args, **kwds)

        new_f.func_name = f.func_name
        return new_f

    return check_accepts


class BitMap():
    """
    Initializes a bitmap with the first bit set to 1
    """

    def __init__(self, bits: int):
        """
        :param bits: number of bits you want to have in bitmap
        :return: None
        """
        self.bitmap = 2 ** (bits - 1)

    def set_bit(self, bit_pos):
        """
        :param bit_pos: bit position from the left. e.g - 0 would change the very left bit to 1
        :return: None
        """
        self.bitmap |= 2 ** 1023 >> bit_pos

    def to_string(self):
        return bin(self.bitmap)[2:]

    def show_bitmap(self):
        string = "{:b}".format(self.bitmap)
        print(string)


class PMemory:
    """
    Physical Memory representation with 1024 frames of 512 words (integers) each
    Implemented as a flat array of integers
    """

    def __init__(self):
        self.PM = [0] * (FRAMESIZE * TOTALFRAMES)  # 512 words (integers) for each of the 1024 frames
        self.bitmap = BitMap(TOTALFRAMES)

    # @accepts(PMemory, int, int)
    def set_PT(self, s: int, f: int):
        """
        Sets an uninitialized frame to be a page table.
            1. Set the segment number to the page table address (first frame)
            2. Allocate two frames for the page table by:
                - setting specified frame pages to all 0s
                - allocating the bitmap
        :param s: segment number
        :param f: page table address (not frame # but should be multiple of 512 to indicate start of frame)
        :return: None
        """
        # Integer Array operations
        self.PM[s] = f
        for i in range(f, f + 2*FRAMESIZE):
            self.PM[i] = 0


        # Bitmap operations
        frame_num = int(f / FRAMESIZE)
        self.bitmap.set_bit(frame_num)
        self.bitmap.set_bit(frame_num + 1)



