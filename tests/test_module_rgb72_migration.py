import hashlib
import json
import os
import shutil
import tempfile
import unittest
from argparse import Namespace

from tifinity.modules import rgb72_migration
from tifinity.parser.tiff import Tiff


class TestModuleRgb72Migration(unittest.TestCase):
    """ Tests relating to the rgb72_to_rgb96 module. """

    def setUp(self):
        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Remove the directory after the test
        shutil.rmtree(self.test_dir)

    @staticmethod
    def _hash_data(data, alg="md5"):
        """Returns the hash value of the specified data using the specified hashing algorithm"""
        m = hashlib.new(alg)
        m.update(data)
        return m.hexdigest()

    def test_one_strip_uncompressed(self):
        """Tests the conversion of a single strip TIFF"""
        from_res_path = "stripes_one_strip_rgb72"
        from_path = os.path.join("./resources", from_res_path)
        args = Namespace(path=[os.path.join(from_path, from_res_path + ".tif")], output=self.test_dir)

        # Do the migration
        rgb72_migration.module.process_cli(args)

        # Calculate hash value of migrated TIFF in temp folder
        migratedTiff = Tiff(os.path.join(self.test_dir, from_res_path+".tif.conv.tif"))
        migratedTiff_img_cs = TestModuleRgb72Migration._hash_data(migratedTiff.ifds[0].img_data)

        # Load the expected results checksum JSON file
        to_res_path = from_res_path[:-2]+"96"
        to_path = os.path.join("./resources", to_res_path)
        with open(os.path.join(to_path, "checksums.json"), 'r') as cs_file:
            to_js = json.load(cs_file)

        # check the checksums are correct
        self.assertEqual(to_js["md5"]["images"][0], migratedTiff_img_cs)

    def test_one_strip_uncompressed_folder(self):
        """Tests the conversion of a single strip TIFF contained in a folder"""
        from_res_path = "stripes_one_strip_rgb72"
        from_path = os.path.join("./resources", from_res_path)
        args = Namespace(path=[from_path], output=self.test_dir)

        # Do the migration
        rgb72_migration.module.process_cli(args)

        # Calculate hash value of migrated TIFF in temp folder
        migratedTiff = Tiff(os.path.join(self.test_dir, from_res_path+".tif.conv.tif"))
        migratedTiff_img_cs = TestModuleRgb72Migration._hash_data(migratedTiff.ifds[0].img_data)

        # Load the expected results checksum JSON file
        to_res_path = from_res_path[:-2]+"96"
        to_path = os.path.join("./resources", to_res_path)
        with open(os.path.join(to_path, "checksums.json"), 'r') as cs_file:
            to_js = json.load(cs_file)

        # check the checksums are correct
        self.assertEqual(to_js["md5"]["images"][0], migratedTiff_img_cs)


if __name__ == '__main__':
    unittest.main()
