import os
import unittest
from argparse import Namespace
from tifinity.modules import compare_tiffs


class TestModuleCompareTiffs(unittest.TestCase):
    """ Tests related to the compare_tiffs module

     Tests:
     * Check for error with only 1 file supplied
     * Compare pixel hash of two identical files"""

    def test_one_file_supplied(self):
        """ Tests that if only a single file is supplied, an appropriate error is returned """
        res_path = "t_one_strip"
        path = os.path.join("./resources", res_path)
        file = os.path.join(path, res_path + ".tiff")
        args = Namespace(tiff1=file)

        with self.assertRaises(AttributeError):
            compare_tiffs.module.process_cli(args)

    def test_identical_file(self):
        """ Tests that pixel checksums are identical if two identical files are supplied """
        res_path = "t_one_strip"
        path = os.path.join("./resources", res_path)
        file = os.path.join(path, res_path + ".tiff")
        args = Namespace(tiff1=file, tiff2=file, metric="checksum")
        output = compare_tiffs.module.process_cli(args)

        self.assertEqual({'Files Identical': True}, output)

    def test_different_files(self):
        """ Tests that different TIFFs return correct output """
        orig_res_path = "t_one_strip"
        orig_path = os.path.join("./resources", orig_res_path)
        orig_file = os.path.join(orig_path, orig_res_path + ".tiff")

        comp_res_path = "t_two_strips_seq_reverse"
        comp_path = os.path.join("./resources", comp_res_path)
        comp_file = os.path.join(comp_path, comp_res_path + ".tiff")

        args = Namespace(tiff1=orig_file, tiff2=comp_file, metric="checksum")
        output = compare_tiffs.module.process_cli(args)

        self.assertEqual({'Files Identical': False,
                          'Images Identical': {0: [False]}}, output)

if __name__ == '__main__':
    unittest.main()
