__author__ = 'Michael'

import unittest
from VirtualMemory import *


class VirtualMemoryTest(unittest.TestCase):
    def setUp(self):
        self.bitmap = BitMap(1024)
        self.mem = PMemory()

    def test_bitmap(self):
        print('\n\n **** TESTING test_{} ******'.format("bitmap"))

        self.bitmap.set_bit(1023)
        self.assertEqual(self.bitmap.bitmap, 2 ** 1023 + 1)
        self.bitmap.show_bitmap()

        self.bitmap.bitmap = 2**1023
        self.bitmap.set_bit(1)
        self.assertEqual(self.bitmap.bitmap, 2 ** 1023 + 2 ** 1022)

        self.bitmap.show_bitmap()

    def test_addPT(self):
        print('\n\n **** TESTING test_{} ******'.format("addPT"))
        print(self.mem.PM[0:512])
        self.mem.set_PT(15, 512)
        print(self.mem.PM[0:512])
        self.assertEqual(self.mem.PM[15], 512)
        print((self.mem.bitmap.to_string()))
        frame_loc = 1
        self.assertEqual(self.mem.bitmap.to_string()[frame_loc], str(1))
        self.assertEqual(self.mem.bitmap.to_string()[frame_loc+1], str(1))

    def test_search_free_frame(self):
        print('\n\n **** TESTING test_{} ******'.format("search_free_frame"))
        print('First Free Frame', self.mem.search_free_frame(True))
        self.assertEquals(self.mem.search_free_frame(True), 512)
        self.assertEquals(self.mem.bitmap.search_free_frame(True), 512)

    def test_first_test_case(self):
        print('\n\n **** TESTING test_{} ******'.format("first_test_case"))
        self.mem.bitmap.show_bitmap()

        self.mem.set_PT(2, 2048)
        self.mem.bitmap.show_bitmap()

        self.mem.set_page(0, 2, 512)
        self.mem.bitmap.show_bitmap()

        self.assertEquals(self.mem.PM[2048], 512)
        self.assertEquals(self.mem.PM[2], 2048)
        self.assertEquals(self.mem.bitmap.to_string()[4], str(1))
        self.assertEquals(self.mem.bitmap.to_string()[1], str(1))

        self.mem.bitmap.show_bitmap()
        print(self.mem.PM[0:512])
    def test_va(self):
        print('\n\n **** TESTING test_{} ******'.format("va"))

        self.va = VA(10485767)
        print(self.va.s)
        print(self.va.p)
        print(self.va.w)
