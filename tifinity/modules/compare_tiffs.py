import json

from tifinity.actions.checksum import Checksum
from tifinity.modules import BaseModule
from tifinity.parser.tiff import Tiff
from tifinity.scripts.timing import time_usage

class CompareTiffs(BaseModule):
    """ Module comparing the similarity of two TIFF files according to some metric.
        Currently only comparison via the MD5 checksums of the file & pixel data is supported."""

    def __init__(self):
        self.cli_name = 'compare'
        self.metric_choices = ['checksum', 'checksum-images']      # other metric choices may be added
        # defaults
        self.json = False

    def add_subparser(self, mainparser):
        m_parser = mainparser.add_parser(self.cli_name)
        m_parser.set_defaults(func=self.process_cli)

        m_parser.add_argument("-m", "--metric", dest="metric", choices=self.metric_choices, required=True)

        m_parser.add_argument("--json", dest="json", action="store_true", help="output in json format")

        m_parser.add_argument("tiff1", help="the original TIFF file to compare")
        m_parser.add_argument("tiff2", help="the comparison TIFF file")

    #@time_usage
    def process_cli(self, args):
        try:
            # Load TIFFs
            tiffs = [Tiff(args.tiff1), Tiff(args.tiff2)]
        except AttributeError:
            raise

        self.returnValues = {}

        # calculate checksums
        if args.metric=="checksum":
            checksums = [Checksum.checksum(t) for t in tiffs]

            # identical files?
            self.returnValues["Files Identical"] = False
            if checksums[0]["full"] == checksums[1]["full"]:
                self.returnValues["Files Identical"] = True

        elif args.metric=="checksum-images":
            checksums = [Checksum.checksum(t, justimage=True) for t in tiffs]

        image_identical = {}
        i = 0
        for i_orig in checksums[0]["images"]:
            image_identical[i] = []                             # for each image in the original TIFF
            for i_other in checksums[1]["images"]:
                image_identical[i].append(i_orig == i_other)    # compare against each image in the comparison TIFF
            i += 1
        self.returnValues["Images Identical"] = image_identical

        output = self.format_output(args.json)
        print(output)
        return output

    def format_output(self, jsonout=False):
        if jsonout:
            return json.dumps(self.returnValues)
        else:
            out = ""
            if "Files Identical" in self.returnValues:
                out += "Files Identical:\t{ident}\n".format(ident=self.returnValues["Files Identical"])
            for x in sorted(self.returnValues["Images Identical"].keys()):
                count=0
                for y in self.returnValues["Images Identical"][x]:
                    out += "Tiff[1].Image[{id}] - Tiff[2].Image[{idy}]:\t{ident}\n".format(id=x, idy=count, ident=y)
                    count+=1

            return out

module = CompareTiffs()     # initiate module class when module imported
