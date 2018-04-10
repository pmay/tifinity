"""
Module to perform a migration on a TIFF encoded to 24 bits per channel (i.e. 72 bits per pixel).
Such TIFFs typically occur through being saved as 24 bit TIFFs in Photoshop.
"""
import os

from tifinity.modules import BaseModule

from tifinity.parser.tiff import Tiff
from tifinity.parser.errors import InvalidTiffError
from tifinity.actions.rgb72_to_rgb96 import rgb72_to_rgb96
from tifinity.scripts.timing import *


class MigrateRGB72(BaseModule):
    def __init__(self):
        self.cli_name = 'migrate_rgb72'
        self.rgb72migrate = rgb72_to_rgb96()

    def add_subparser(self, mainparser):
        m_parser = mainparser.add_parser(self.cli_name)
        m_parser.set_defaults(func=self.process_cli)
        m_parser.add_argument("path", nargs="+", help="the TIFF file or folder(s) containing TIFFs to migrate.")

    def process_cli(self, args):
        for path in args.path:
            files = [path]                          # assume path=file to start with

            if os.path.isdir(path):
                files = [x.path for x in os.scandir(path)]

            for file in files:
                self.__migrate_tiff(file, file + ".conv.tif")

    def __migrate_tiff(self, fromfile, to_file):
        print("Migrating " + fromfile, end='')

        try:
            tiff = Tiff(fromfile)

            # Convert image data
            migrated = self.rgb72migrate.migrate(tiff)

            # Write new TIFF if at least one sub-image has been migrated
            if migrated:
                print("\t\tDone")
                tiff.save_tiff(to_file)
            else:
                print("\t\tNot migrated (No need)")
        except InvalidTiffError:
            print("\t\tNot migrated (Invalid TIFF/Not a TIFF)")


module = MigrateRGB72()  # initiate module class when module imported
