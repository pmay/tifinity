import os

from tifinity.modules import BaseModule

from tifinity.parser.tiff import Tiff
from tifinity.parser.tiff import inv_ifdtag

class TiffDetails(BaseModule):
    def __init__(self):
        self.cli_name = 'show_tags'

    def add_subparser(self, mainparser):
        m_parser = mainparser.add_parser(self.cli_name)
        m_parser.set_defaults(func=self.process_cli)

        m_parser.add_argument("-t", "--tag", dest="tag", help="the tag name or number to display")

        m_parser.add_argument("file", help="the TIFF file whose tags to show")

    def process_cli(self, args):
        tiff = Tiff(args.file)

        for ifd in tiff.ifds:
            if args.tag:
                try:
                    tag = int(args.tag)
                except ValueError:
                    # it's a string instead
                    tag = args.tag

                ifd.print_ifd_header()
                ifd.print_tag(tag)
            else:
                # print all
                ifd.print_ifd()

module = TiffDetails()  # initiate module class when module imported