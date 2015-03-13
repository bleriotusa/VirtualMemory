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

        n = 1 if consecutive else 0
        bit_string = "{:b}".format(self.bitmap)
        for frame in range(len(bit_string)):
            if bit_string[frame] == '0' and bit_string[frame + n] == '0':
                return frame

        print("NO SLOT FOUND")

    def search_free_frame(self, consecutive):
        return 512 * self.search_free_bit(consecutive)


class VA:
    """
    Takes in an INT as the virtual address and creates a Virtual Address object
    :param va: virtual address in integer form
    """

    def __init__(self, va: int):
        va_string = format(va, '032b')[4:]
        self.s = int(va_string[:9], 2)
        self.p = int(va_string[9:19], 2)
        self.w = int(va_string[19:], 2)

        self.va_string = va_string

    def get_sp(self):
        return int(self.va_string[:19], 2)


class TLB:
    class BufferSlot:
        def __init__(self, LRU: int, sp: int, f: int):
            self.LRU = LRU
            self.sp = sp
            self.f = f

    def __init__(self):
        self.tlb = [TLB.BufferSlot(0, -1000, -1000) for i in range(0, 4)]

    def search_sp(self, sp):
        for slot in self.tlb:
            if slot.sp == sp:
                return slot

    def search_lru(self, lru):
        for slot in self.tlb:
            if slot.LRU == lru:
                return slot
        print("no such lru value: {}".format(lru))

    def lookup(self, sp):
        """
        :param sp: s and p bitstrings combined to int
        :return: f # held by TLB slot with sp if hit, or None if miss
        """
        target_slot = self.search_sp(sp)
        if target_slot:
            f = target_slot.f
            # decrement other values
            for slot in self.tlb:
                if slot.LRU > target_slot.LRU:
                    slot.LRU -= 1
            # set just used LRU to 3
            target_slot.LRU = 3

            # print('hit')
            return target_slot.f

        else:
            # print('miss')
            return None

    def update(self, sp: int, f: int):
        assert type(sp) == int and type(f) == int

        target_slot = self.search_lru(0)
        target_slot.LRU = 3
        target_slot.sp = sp
        target_slot.f = f

        # decrement all other values by 1
        for slot in self.tlb:
            if slot.sp != target_slot.sp and slot.LRU > 0:
                slot.LRU -= 1



class PMemory:
    """
    Physical Memory representation with 1024 frames of 512 words (integers) each
    Implemented as a flat array of integers
    """

    def __init__(self, seg_setup_ints: [(int, int)]=[], pt_setup_ints: [(int, int, int)]=[]):
        self.PM = [0] * (FRAMESIZE * TOTALFRAMES)  # 512 words (integers) for each of the 1024 frames
        self.bitmap = BitMap(TOTALFRAMES)

        for tup in seg_setup_ints:
            s = tup[0]
            f = tup[1]
            self.set_PT(s, f)

        for tup in pt_setup_ints:
            p = tup[0]
            s = tup[1]
            f = tup[2]
            self.set_page(p, s, f)

    def add_page(self, p: int, s: int):
        f = self.bitmap.search_free_frame(False)
        self.set_page(p, s, f)
        # 2. allocate the page
        for i in range(f, f + FRAMESIZE):
            self.PM[i] = 0
        return f

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
        except AssertionError as e:
            print('error', e, {'p': p, 's': s, 'f': f})
            return 'err'

        # PM operations (of the main INT array)
        # 1. set page # given by PM[PM[s] + p] to the page address given
        self.PM[self.PM[s] + p] = f
        if f != -1:
            # Bitmap operations - set the appropriate bit to be set
            frame_num = int(f / FRAMESIZE)
            self.bitmap.set_bit(frame_num)

        print('PM[{}] is now {}'.format(self.PM[s] + p, f))

    def add_PT(self, s: int) -> int:
        f = self.bitmap.search_free_frame(True)
        self.set_PT(s, f)
        # 2. allocate the frames
        for i in range(f, f + 2 * FRAMESIZE):
            self.PM[i] = 0
        return f

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
            print('error', AssertionError)
            return

        # PM operations (of the main INT array)
        # 1. set segment # to the PT address given
        self.PM[s] = f
        if f != -1:
            # Bitmap operations - set the appropriate bit to be set
            frame_num = int(f / FRAMESIZE)
            self.bitmap.set_bit(frame_num)
            self.bitmap.set_bit(frame_num + 1)

        print('PM[{}] is now {}'.format(s, f))

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


class VMemSystem:
    """
    System for managing the Physical Memory Representation (driver)
    """

    def __init__(self, seg_setup_ints: [(int, int)], pt_setup_ints: [(int, int, int)], use_tlb: bool):
        self.PM = PMemory(seg_setup_ints, pt_setup_ints)

        self.use_tlb = use_tlb
        if use_tlb:
            self.tlb = TLB()

    def read(self, va):
        vaddress = VA(va)
        s = vaddress.s
        p = vaddress.p
        w = vaddress.w

        if self.use_tlb:
            f = self.tlb.lookup(vaddress.get_sp())
            if f: # then hit
                print('hit')
                output_file.write('h ')
                return f + w

        PM = self.PM.PM
        print('reading from {} + {} = {}, got {}'.format(PM[s], p, PM[s] + p, PM[PM[s] + p]))

        if PM[s] == -1:
            return 'pf'

        elif PM[s] == 0:
            return 'err'

        if PM[PM[s] + p] == -1:
            return 'pf'

        elif PM[PM[s] + p] == 0:
            return 'err'

        PA = PM[PM[s] + p] + w

        if self.use_tlb:
            self.tlb.update(vaddress.get_sp(), PA - w)
            print('miss')
            output_file.write('m ')

        # print(PA)
        return PA

    def write(self, va):
        vaddress = VA(va)
        s = vaddress.s
        p = vaddress.p
        w = vaddress.w

        if self.use_tlb:
            f = self.tlb.lookup(vaddress.get_sp())
            if f: # then hit
                print('hit')
                output_file.write('h ')
                return f + w

        PM = self.PM.PM

        if PM[s] == -1:
            return 'pf'

        elif PM[s] == 0:
            self.PM.add_PT(s)

        if PM[PM[s] + p] == -1:
            return 'pf'

        elif PM[PM[s] + p] == 0:
            self.PM.add_page(p, s)

        print('writing to {} + {} = {}, got {}'.format(PM[s], p, PM[s] + p, PM[PM[s] + p]))

        PA = PM[PM[s] + p] + w

        if self.use_tlb:
            self.tlb.update(vaddress.get_sp(), PA - w)
            print('miss')
            output_file.write('m ')
        # print(PA)
        return PA


def parse_doubles(l: [int]) -> [(int, int)]:
    tuples = []
    for i in range(0, len(l), 2):
        s = l[i]
        f = l[i + 1]
        tuples.append((s, f))

    return tuples


def parse_triples(l: [int]) -> [(int, int, int)]:
    tuples = []
    for i in range(0, len(l), 3):
        tuples.append((l[i], l[i + 1], l[i + 2]))

    return tuples


if __name__ == '__main__':
    TLB_ON = True
    test_num = 2
    setup_filename = 'tests/input{}_{}.txt'.format(test_num, 1)
    command_filename = 'tests/input{}_{}.txt'.format(test_num, 2)
    output_filename = 'tests/myoutput{}_{}.txt'.format(test_num, 1 if not TLB_ON else 2)

    setup_file = open(setup_filename)
    command_file = open(command_filename)
    output_file = open(output_filename, 'w+')

    # retrieve a list of lists, where each list is an array of the ints in the file
    setup_commands = []
    line = True
    while True:
        line = setup_file.readline()
        if line == '':
            break
        setup_commands.append(map(lambda x: int(x), line.split(' ')))

    seg_setup_ints = parse_doubles(list(setup_commands[0]))
    pt_setup_ints = parse_triples(list(setup_commands[1]))

    # print(seg_setup_ints)
    # print(pt_setup_ints)

    # END init parsing
    vm = VMemSystem(seg_setup_ints, pt_setup_ints, TLB_ON)

    cf = command_file.readline()
    command_list = list(map(lambda x: int(x), cf.strip().split(' ')))
    command_tups = parse_doubles(command_list)
    # print(command_tups)

    for t in command_tups:
        if t[0] == 0:
            out = str(vm.read(t[1]))
            output_file.write(out)
        else:
            out = str(vm.write(t[1]))
            output_file.write(out)

        output_file.write(' ')

    output_file.close()