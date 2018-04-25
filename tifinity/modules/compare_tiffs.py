from tifinity.actions.checksum import Checksum
from tifinity.modules import BaseModule
from tifinity.parser.tiff import Tiff


class CompareTiffs(BaseModule):
    """ Module comparing the similarity of two TIFF files.
        By default this compares the MD5 checksums of the pixel image data. """

    ModuleReturnCodes = {
        "Identical": 0,
        "Different": 1,
        "NotEnoughFiles": 2}

    def __init__(self):
        self.cli_name = 'compare'
        self.returnValues = {}

    def add_subparser(self, mainparser):
        m_parser = mainparser.add_parser(self.cli_name)
        m_parser.set_defaults(func=self.process_cli)
        m_parser.add_argument("tiff1", help="the original TIFF file to compare")
        m_parser.add_argument("tiff2", help="the comparison TIFF file")

    def process_cli(self, args):
        print(args.files)
        if len(args.files) < 2:
            print("More than one file is required for comparison")
            return self.ModuleReturnCodes["NotEnoughFiles"]

        # Load TIFFs
        tiffs = [Tiff(f) for f in args.files]

        # calculate checksums
        checksums = [Checksum.checksum(t) for t in tiffs]

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
