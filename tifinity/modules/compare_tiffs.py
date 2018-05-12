from tifinity.actions.checksum import Checksum
from tifinity.modules import BaseModule
from tifinity.parser.tiff import Tiff


class CompareTiffs(BaseModule):
    """ Module comparing the similarity of two TIFF files according to some metric.
        Currently only comparison via the MD5 checksums of the file & pixel data is supported."""

    def __init__(self):
        self.cli_name = 'compare'
        self.metric_choices = ["checksum"]      # other metric choices may be added

    def add_subparser(self, mainparser):
        m_parser = mainparser.add_parser(self.cli_name)
        m_parser.set_defaults(func=self.process_cli)

        m_parser.add_argument("-m", "--metric", dest="metric", choices=self.metric_choices, required=True)

        m_parser.add_argument("tiff1", help="the original TIFF file to compare")
        m_parser.add_argument("tiff2", help="the comparison TIFF file")

    def process_cli(self, args):
        # if args.tiff1 is None or args.tiff2 is None:
        #     print("Two files are required for comparison")
        #     return self.ModuleReturnCodes["NotEnoughFiles"]

        try:
            # Load TIFFs
            tiffs = [Tiff(args.tiff1), Tiff(args.tiff2)]
        except AttributeError:
            raise

        # calculate checksums
        if args.metric=="checksum":
            checksums = [Checksum.checksum(t) for t in tiffs]

            self.returnValues = {}

            # identical files?
            if checksums[0]["full"]==checksums[1]["full"]:
                self.returnValues["Files Identical"] = True
                print ("Files Identical")
                return self.returnValues

            self.returnValues["Files Identical"] = False
            image_identical = {}
            i = 0
            for i_orig in checksums[0]["images"]:
                image_identical[i] = []                             # for each image in the original TIFF
                for i_other in checksums[1]["images"]:
                    image_identical[i].append(i_orig == i_other)    # compare against each image in the comparison TIFF
                i += 1
            self.returnValues["Images Identical"] = image_identical

            return self.returnValues

module = CompareTiffs()     # initiate module class when module imported
