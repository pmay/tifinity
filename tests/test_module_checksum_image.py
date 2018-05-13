import json
import os
import unittest
from argparse import Namespace
from tifinity.modules import checksum_image

class TestModuleChecksumImage(unittest.TestCase):
    """Tests relating to checksum_image module

    Tests:
    *  1) File, Image and IFD MD5 check for single strip little-endian (LE) TIFF
    *  2) File, Image and IFD MD5 check for sequential 2-strip LE TIFF with strips referenced in sequential order
    *  3) File, Image and IFD MD5 check for sequential 2-strip LE TIFF with strips referenced in reverse order
    *  4) File, Image and IFD MD5 check for non-sequential 2-strip LE TIFF with strips referenced in sequential order
    *  5) File, Image and IFD MD5 check for non-sequential 2-strip LE TIFF with strips referenced in reverse order
    *  6) File, Image and IFD MD5 check for compressed single strip LE TIFF
    *  7) File, Image and IFD MD5 check for single strip bilevel LE TIFF
    *  8) File, Image and IFD MD5 check for two subfile single strip LE TIFF
    *  9) File, Image and IFD MD5 check for single strip LE TIFF with exif metadata.
    * 10) File, Image and IFD MD5 check for single strip big-endian TIFF

    Todo: Other tests
    *  Check MD5 for non-image data for single strip TIFF
    *  Check MD5 for non-image data for a two strip TIFF
    """

    def _evaluate_checksums(self, res_path):
        path = os.path.join("./resources", res_path)
        args = Namespace(algorithm="md5", json=True, file=os.path.join(path, res_path+".tiff"))
        output_js = json.loads(checksum_image.module.process_cli(args))

        # load json checksum file
        with open(os.path.join(path, "checksums.json"), 'r') as cs_file:
            gt_js = json.load(cs_file)

        # check the checksums are correct
        self.assertEqual(output_js["full"], gt_js["md5"]["full"])
        self.assertEqual(output_js["images"], gt_js["md5"]["images"])
        self.assertEqual(output_js["ifds"], gt_js["md5"]["ifds"])

    def test_single_strip_checksums(self):
        """Tests that the full TIFF file's checksum and those for the sub-image is correct for a single strip image"""
        self._evaluate_checksums("t_one_strip")

    def test_two_strips_seq_checksums(self):
        """ Tests the checksums for a TIFF file with an image split into two sequential strips.
            TIFF containing two Strips of RGB data in sequential order (i.e. within the file
            the Strips are ordered by top half of image followed by bottom half) and the
            Strips are referenced in Strip order.
            Image looks like a blue 'T' on a red (top) and green (bottom) background.
        """
        self._evaluate_checksums("t_two_strips_seq")

    def test_two_strips_reverse_seq_checksums(self):
        """ Tests the checksums for a TIFF file with an image split into two sequential strips
            referenced in reverse.
            TIFF containing two Strips of RGB data in sequential order (i.e. within the file
            the Strips are ordered by top half of image followed by bottom half) and the
            Strips are referenced in reverse Strip order (i.e. 2nd Strip comes first)
            Image looks like a split 'T' with the lower stem on a green background appearing above
            the red crossbar on a red background.
        """
        self._evaluate_checksums("t_two_strips_seq_reverse")

    def test_two_strips_non_seq_checksums(self):
        """ Tests the checksums for a TIFF file with an image split into two non-sequential strips.
            TIFF containing two Strips of RGB data in non-sequential order (i.e. within the
            file the Strips are ordered by bottom half of image followed by top half) and the
            Strips are referenced in Strip order (i.e. bottom of image appears at the top).
            Image looks like a split 'T' with the lower stem on a green background appearing above
            the red crossbar on a red background.
        """
        self._evaluate_checksums("t_two_strips_non_seq")

    def test_two_strips_reverse_non_seq_checksums(self):
        """ Tests the checksums for a TIFF file with an image split into two non-sequential strips.
            TIFF containing two Strips of RGB data in non-sequential order (i.e. within the
            file the Strips are ordered by bottom half of image followed by top half) and the
            Strips are referenced in reverse Strip order (i.e. 2nd Strip comes first)
            Image looks like a blue 'T' over a red background (top half) and a green background(bottom half).
        """
        self._evaluate_checksums("t_two_strips_non_seq_reverse")

    def test_single_strip_compressed_lzw(self):
        """ Tests the checksums for a TIFF file with a LZW compressed image in a single strip of RGB data. """
        self._evaluate_checksums("t_one_strip_compressed_lzw")

    def test_single_strip_bilevel(self):
        """ Tests the checksums for a single strip bilevel TIFF """
        self._evaluate_checksums("t_one_strip_bilevel")

    def test_two_subfiles_single_strip(self):
        """ Tests the checksums for a TIFF file containing two single-strip images. """
        self._evaluate_checksums("t_two_subfiles_one_strip")

    def test_single_strip_with_exif_checksum(self):
        """ Tests the checksums for a single strip TIFF file with exif metadata. """
        self._evaluate_checksums("t_one_strip_with_exif")

    def test_single_strip_big_endian_checksum(self):
        """ Tests the checksums for a single strip big-endian TIFF file """
        self._evaluate_checksums("t_one_strip_big_endian")

if __name__ == '__main__':
    unittest.main()
