__author__ = 'Michael'

import unittest
from VirtualMemory import *


class VirtualMemoryTest(unittest.TestCase):
    def setUp(self):
        self.bitmap = BitMap(1024)
        self.mem = PMemory()

    def test_bitmap(self):
        self.bitmap.set_bit(1023)
        self.assertEqual(self.bitmap.bitmap, 2 ** 1023 + 1)

        self.bitmap.bitmap = 2**1023
        self.bitmap.set_bit(1)
        self.assertEqual(self.bitmap.bitmap, 2 ** 1023 + 2 ** 1022)

    def test_addPT(self):
        print(' **** TESTING test_{} ******'.format("addPT"))
        print(self.mem.PM[0:512])
        self.mem.set_PT(15, 512)
        print(self.mem.PM[0:512])
        self.assertEqual(self.mem.PM[15], 512)
        print((self.mem.bitmap.to_string()))
        frame_loc = 1
        self.assertEqual(self.mem.bitmap.to_string()[frame_loc], str(1))
        self.assertEqual(self.mem.bitmap.to_string()[frame_loc+1], str(1))

