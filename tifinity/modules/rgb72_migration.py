"""
Module to perform a migration on a TIFF encoded to 24 bits per channel (i.e. 72 bits per pixel).
Such TIFFs typically occur through being saved as 24 bit TIFFs in Photoshop.
"""
import os

from tifinity.parser.tiff import Tiff
from tifinity.actions.rgb72_to_rgb96 import rgb72_to_rgb96
from tifinity.scripts.timing import *


class migrate_rgb72():
    def __init__(self):
        self.cli_name = 'migrate_rgb72'
        self.cli_args = [{'name': "path", 'nargs':"+", 'help':"the TIFF file or folder(s) containing TIFFs to migrate."}]
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

    @time_usage
    def __migrate_tiff(self, fromfile, to_file):
        print("Migrating " + fromfile)

        tiff = Tiff(fromfile)

        # Convert image data
        self.rgb72migrate.migrate(tiff)

        # Write new TIFF
        tiff.save_tiff(to_file)


module = migrate_rgb72()  # initiate module class when module imported
