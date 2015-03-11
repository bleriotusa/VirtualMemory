__author__ = 'Michael'

from unittest import TestCase

FRAMESIZE = 512
TOTALFRAMES = 1024
TOTALWORDS = FRAMESIZE * TOTALFRAMES


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

    def __init__(self, bits=TOTALFRAMES):
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

    def search_free_bit(self, consecutive):
        """
        Searches for a free n consecutive # of frames together and returns the index
        n = 2 if conseq is True else 1
        :param consecutive: Condition for which you want 2 consecutive frames or 1
        :return: index of the first frame found
        """

        n = 1 if bool else 0
        bit_string = "{:b}".format(self.bitmap)
        for frame in range(len(bit_string)):
            if bit_string[frame] == 0 and bit_string[frame + n] == 0:
                return frame



class PMemory:
    """
    Physical Memory representation with 1024 frames of 512 words (integers) each
    Implemented as a flat array of integers
    """

    def __init__(self):
        self.PM = [0] * (FRAMESIZE * TOTALFRAMES)  # 512 words (integers) for each of the 1024 frames
        self.bitmap = BitMap(TOTALFRAMES)

    def set_page(self, p: int, s: int, f: int):
        """
        Sets an uninitialized frame to be a page.
        :param p: page # within page table
        :param s: segment #
        :param f: frame address (word/int address in int array)
        :return: None
        """
        try:
            TestCase().assertLess(p, FRAMESIZE * 2)
            TestCase().assertLess(s, FRAMESIZE)
            TestCase().assertLess(f, TOTALWORDS)
        except AssertionError:
            print('error')



    # @accepts(PMemory, int, int)
    def set_PT(self, s: int, f: int):
        """
        Sets an uninitialized frame to be a page table.
            1. Set the segment number to the page table address (first frame)
            2. Allocate two frames for the page table by:
                - setting specified frame pages to all 0s
                - allocating the bitmap
        :param s: segment number
        :param f: page table address (not frame # but word #. should be multiple of 512 to indicate start of frame)
        :return: None
        """
        try:
            TestCase().assertLess(s, FRAMESIZE)
            TestCase().assertLess(f, TOTALWORDS)
        except AssertionError:
            print('error')

        # PM operations (of the main INT array)
        # 1. set segment # to the PT address given
        # 2. allocate the frames
        self.PM[s] = f
        for i in range(f, f + 2 * FRAMESIZE):
            self.PM[i] = 0


        # Bitmap operations - set the appropriate bit to be set
        frame_num = int(f / FRAMESIZE)
        self.bitmap.set_bit(frame_num)
        self.bitmap.set_bit(frame_num + 1)

    def search_free_frame(self, conseq: bool) -> int:
        """
        Searches for a free n consecutive # of frames together and returns the index
        n = 2 if conseq is True else 1
        :param conseq: Condition for which you want 2 consecutive frames or 1
        :return: index of the first frame found
        """
        n = 1 if bool else 0

        for frame in range(512, TOTALWORDS, 512):
            if self.PM[frame] == 0 and self.PM[frame + n] == 0:
                return frame


