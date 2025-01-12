#!/usr/bin/env python3

from seamcarver import *
from PIL import Image
import unittest

class SeamCarverTester(unittest.TestCase):
    def sctest_000_calculate_energy_ex1(self):
        'Calculate energy of a non-border pixel (1, 2) from example 1'
        ex1 = SeamCarver(Image.open('data/3x4.png'))
        out = ex1.energy(1, 2)
        self.assertAlmostEqual(out, 228.0877024)

    def sctest_001_calculate_energy_ex1(self):
        'Calculate energy of a border pixel (1, 0) from example 1'
        ex1 = SeamCarver(Image.open('data/3x4.png'))
        out = ex1.energy(1, 0)
        self.assertAlmostEqual(out, 228.0789337)

    def sctest_002_calculate_energy_ex1(self):
        'Calculate energy of pixel (1, 1) from example 1'
        ex1 = SeamCarver(Image.open('data/3x4.png'))
        out = ex1.energy(1, 1)
        self.assertAlmostEqual(out, 228.5278976)

    def sctest_003_find_vertical_seam_ex3(self):
        'Find vertical seam from example 3'
        ex3 = SeamCarver(Image.open('data/6x5.png'))
        seam = ex3.find_vertical_seam()
        self.assertEqual(seam, [3, 4, 3, 2, 2])

    def sctest_004_find_horizontal_seam_ex3(self):
        'Find horizontal seam from example 3'
        ex3 = SeamCarver(Image.open('data/6x5.png'))
        seam = ex3.find_horizontal_seam()
        self.assertEqual(seam, [2, 2, 1, 2, 1, 2])

    def sctest_005_remove_vertical_seam_ex3(self):
        'Remove vertical seam from example 3'
        ex3 = SeamCarver(Image.open('data/6x5.png'))
        seam = ex3.find_vertical_seam()
        ex3.remove_vertical_seam(seam)
        self.assertEqual(ex3.width(), 5, 'width is not 5')
        self.assertEqual(ex3.height(), 5, 'height is not 5')
        carved = {(0, 0): (78, 209, 79), (1, 0): (63, 118, 247), (2, 0): (92, 175, 95), (3, 0): (210, 109, 104), (4, 0): (252, 101, 119),
                  (0, 1): (224, 191, 182), (1, 1): (108, 89, 82), (2, 1): (80, 196, 230), (3, 1): (112, 156, 180), (4, 1): (142, 151, 142),
                  (0, 2): (117, 189, 149), (1, 2): (171, 231, 153), (2, 2): (149, 164, 168), (3, 2): (120, 105, 138), (4, 2): (163, 174, 196),
                  (0, 3): (163, 222, 132), (1, 3): (187, 117, 183), (2, 3): (158, 143, 79), (3, 3): (220, 75, 222), (4, 3): (189, 73, 214),
                  (0, 4): (211, 120, 173), (1, 4): (188, 218, 244), (2, 4): (163, 166, 246), (3, 4): (79, 125, 246), (4, 4): (211, 201, 98)}
        for i, j in ex3.keys():
            self.assertEqual(ex3[i, j], carved[i, j], f'pixel {i, j} does not match')

    def sctest_006_remove_horizontal_seam_ex3(self):
        'Remove horizontal seam from example 3'
        ex3 = SeamCarver(Image.open('data/6x5.png'))
        seam = ex3.find_horizontal_seam()
        ex3.remove_horizontal_seam(seam)
        self.assertEqual(ex3.width(), 6, 'width is not 6')
        self.assertEqual(ex3.height(), 4, 'height is not 4')
        carved = {(0, 0): (78, 209, 79), (1, 0): (63, 118, 247), (2, 0): (92, 175, 95), (3, 0): (243, 73, 183), (4, 0): (210, 109, 104), (5, 0): (252, 101, 119),
                  (0, 1): (224, 191, 182), (1, 1): (108, 89, 82), (2, 1): (149, 164, 168), (3, 1): (112, 156, 180), (4, 1): (120, 105, 138), (5, 1): (142, 151, 142),
                  (0, 2): (163, 222, 132), (1, 2): (187, 117, 183), (2, 2): (92, 145, 69), (3, 2): (158, 143, 79), (4, 2): (220, 75, 222), (5, 2): (189, 73, 214),
                  (0, 3): (211, 120, 173), (1, 3): (188, 218, 244), (2, 3): (214, 103, 68), (3, 3): (163, 166, 246), (4, 3): (79, 125, 246), (5, 3): (211, 201, 98)}
        for i, j in ex3.keys():
            self.assertEqual(ex3[i, j], carved[i, j], f'pixel {i, j} does not match')

    def sctest_007_remove_second_vertical_seam_ex3(self):
        'Remove second vertical seam from example 3'
        ex3 = SeamCarver(Image.open('data/6x5.png'))
        seam = ex3.find_vertical_seam()
        ex3.remove_vertical_seam(seam)
        seam = ex3.find_vertical_seam()
        ex3.remove_vertical_seam(seam)
        self.assertEqual(ex3.width(), 4, 'width is not 5')
        self.assertEqual(ex3.height(), 5, 'height is not 5')
        carved = {(0, 0): (78, 209, 79), (1, 0): (63, 118, 247), (2, 0): (92, 175, 95), (3, 0): (252, 101, 119),
                  (0, 1): (224, 191, 182), (1, 1): (108, 89, 82), (2, 1): (112, 156, 180), (3, 1): (142, 151, 142),
                  (0, 2): (117, 189, 149), (1, 2): (149, 164, 168), (2, 2): (120, 105, 138), (3, 2): (163, 174, 196),
                  (0, 3): (163, 222, 132), (1, 3): (187, 117, 183), (2, 3): (220, 75, 222), (3, 3): (189, 73, 214),
                  (0, 4): (211, 120, 173), (1, 4): (188, 218, 244), (2, 4): (79, 125, 246), (3, 4): (211, 201, 98)}

        for i, j in ex3.keys():
            self.assertEqual(ex3[i, j], carved[i, j], f'pixel {i, j} does not match')

    def sctest_008_remove_second_horizontal_seam_ex3(self):
        'Remove second horizontal seam from example 3'
        ex3 = SeamCarver(Image.open('data/6x5.png'))
        seam = ex3.find_horizontal_seam()
        ex3.remove_horizontal_seam(seam)
        seam = ex3.find_horizontal_seam()
        ex3.remove_horizontal_seam(seam)
        self.assertEqual(ex3.width(), 6, 'width is not 6')
        self.assertEqual(ex3.height(), 3, 'height is not 3')
        carved = {(0, 0): (78, 209, 79), (1, 0): (63, 118, 247), (2, 0): (92, 175, 95), (3, 0): (112, 156, 180), (4, 0): (210, 109, 104), (5, 0): (252, 101, 119),
                  (0, 1): (224, 191, 182), (1, 1): (187, 117, 183), (2, 1): (92, 145, 69), (3, 1): (158, 143, 79), (4, 1): (220, 75, 222), (5, 1): (189, 73, 214),
                  (0, 2): (211, 120, 173), (1, 2): (188, 218, 244), (2, 2): (214, 103, 68), (3, 2): (163, 166, 246), (4, 2): (79, 125, 246), (5, 2): (211, 201, 98)}
        for i, j in ex3.keys():
            self.assertEqual(ex3[i, j], carved[i, j], f'pixel {i, j} does not match')

    def sctest_009_energy_invalid_values(self):
        'Throw IndexError for invalid values for energy fn'
        ex3 = SeamCarver(Image.open('data/6x5.png'))
        with self.assertRaises(IndexError):
            ex3.energy(0, 6)
        with self.assertRaises(IndexError):
            ex3.energy(0, -1)
        with self.assertRaises(IndexError):
            ex3.energy(-1, 2)
        with self.assertRaises(IndexError):
            ex3.energy(10, 10)

    def sctest_010_remove_vertical_seam_wrong_length(self):
        'Throw SeamError if attempted to remove vertical seam with wrong length'
        ex3 = SeamCarver(Image.open('data/6x5.png'))
        with self.assertRaises(SeamError):
            ex3.remove_vertical_seam([1, 2, 3, 2])

    def sctest_011_remove_horizontal_seam_wrong_length(self):
        'Throw SeamError if attempted to remove horizontal seam with wrong length'
        ex3 = SeamCarver(Image.open('data/6x5.png'))
        with self.assertRaises(SeamError):
            ex3.remove_horizontal_seam([1, 2, 3, 2])

    def sctest_012_remove_vertical_seam_invalid(self):
        'Throw SeamError if attempted to remove invalid vertical seam'
        ex3 = SeamCarver(Image.open('data/6x5.png'))
        with self.assertRaises(SeamError):
            ex3.remove_vertical_seam([2, 2, 3, 4, 1])

    def sctest_013_remove_horizontal_seam_invalid(self):
        'Throw SeamError if attempted to remove invalid horizontal seam'
        ex3 = SeamCarver(Image.open('data/6x5.png'))
        with self.assertRaises(SeamError):
            ex3.remove_horizontal_seam([2, 3, 2, 4, 3, 1])

    def sctest_014_remove_vertical_seam_width1(self):
        'Throw SeamError if attempted to remove vertical seam when current width is 1'
        ex1 = SeamCarver(Image.open('data/3x4.png'))
        seam = [0, 0, 0, 0]
        ex1.remove_vertical_seam(seam)
        ex1.remove_vertical_seam(seam)
        with self.assertRaises(SeamError):
            ex1.remove_vertical_seam(seam)

    def sctest_015_remove_horizontal_seam_height1(self):
        'Throw SeamError if attempted to remove horizontal seam when current height is 1'
        ex1 = SeamCarver(Image.open('data/3x4.png'))
        seam = [0, 0, 0]
        for _ in range(3):
            ex1.remove_horizontal_seam(seam)
        with self.assertRaises(SeamError):
            ex1.remove_horizontal_seam(seam)

if __name__ == '__main__':
    unittest.defaultTestLoader.testMethodPrefix = 'sctest'
    unittest.main()
