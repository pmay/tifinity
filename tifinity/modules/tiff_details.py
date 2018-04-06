import os

from tifinity.modules import BaseModule

from tifinity.parser.tiff import Tiff

class TiffDetails(BaseModule):
    def __init__(self):
        self.cli_name = 'detail_tiff'

    def add_subparser(self, mainparser):
        m_parser = mainparser.add_parser(self.cli_name)
        m_parser.set_defaults(func=self.process_cli)
        m_parser.add_argument("file", help="the TIFF file to detail")

    def process_cli(self, args):
        tiff = Tiff(args.file)

        for ifd in tiff.ifds:
            ifd.print_ifd()

module = TiffDetails()  # initiate module class when module imported