import json

from tifinity.actions.checksum import Checksum
from tifinity.modules import BaseModule
from tifinity.parser.tiff import Tiff
from tifinity.scripts.timing import time_usage


class ImageFixity(BaseModule):
    """ Module to perform fixity checks on TIFF files. """
    def __init__(self):
        self.cli_name = 'checksum'
        self.hashes = {}

    def add_subparser(self, mainparser):
        m_parser = mainparser.add_parser(self.cli_name)
        m_parser.set_defaults(func=self.process_cli)
        m_parser.add_argument("-a", "--alg", dest="algorithm", choices=['md5', 'sha256', 'sha512', 'sha3_256', 'sha3_512'],
                              default='sha256', help="the hashing algorithm to use")
        m_parser.add_argument("--json", dest="json", action="store_true", help="output in json format")
        m_parser.add_argument("file", help="the TIFF file to generate checksum values for")

    # @time_usage
    def process_cli(self, args):
        tiff = Tiff(args.file)
        alg = args.algorithm

        self.hashes = Checksum.checksum(tiff, alg)

        output = self.format_output(args.json)
        print(output)
        return output

    def format_output(self, jsonout=False):
        if jsonout:
            return json.dumps(self.hashes)
        else:
            out = "Full File:\t{digest}\n".format(digest=self.hashes["full"])
            count = 0
            for x in self.hashes["images"]:
                out += "Image [{id}]:\t{digest}\n".format(id=count, digest=x)
                count+=1
            return out


module = ImageFixity()  # initiate module class when module imported