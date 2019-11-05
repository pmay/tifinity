from tifinity.actions.icc_parser import IccProfile

from tifinity.modules import BaseModule

from tifinity.parser.tiff import Tiff
from tifinity.parser.tiff import inv_ifdtag

class TiffDetails(BaseModule):
    def __init__(self):
        self.cli_name = 'show_tags'

    def add_subparser(self, mainparser):
        m_parser = mainparser.add_parser(self.cli_name)
        m_parser.set_defaults(func=self.process_cli)

        #m_parser.add_argument("--json", dest="json", action="store_true", help="output in json format")
        m_parser.add_argument("--csv", dest="csv", action="store_true", help="output table in csv format")

        # note: if this is the last optional argument used before the file argument, then either this optional
        #       argument has to be specified *after* the file on the CLI or a "--" has to be used to separate the
        #       tags list from the file argument:
        #        tifinity show_tags <file> -t <tag>
        #       OR
        #        tifinity show_tags -t <tag> -- <file>
        m_parser.add_argument("-t", "--tag", dest="tags", nargs="+", help="the tag name(s) or number(s) to display")
        m_parser.add_argument("--detail", dest="detail", action="store_true",
                              help="print all bytes when values exceed 100 characters")
        # m_parser.add_argument("--expand", dest="expand", action="store_true",
        #                       help="prints the actual value not the hex representation")

        m_parser.add_argument("file", help="the TIFF file whose tags to show")

    @staticmethod
    def _normalise_tag(tag):
        """Normalises the tag to an integer values"""
        try:
            norm_tag = int(tag)
        except ValueError:
            norm_tag = inv_ifdtag.get(tag, None)
        return norm_tag

    def process_cli(self, args):
        tiff = Tiff(args.file)

        numeric_tags = set([])
        image_tags = []
        for ifd in tiff.ifds:
            if args.tags is None:
                # get everything
                directories = ifd.directories
                numeric_tags |= set(directories.keys())

            else:
                # only use the tags specified
                # turn tags to numeric ids, ignoring unknown tags
                numeric_tags |= set([v for v in (TiffDetails._normalise_tag(t) for t in args.tags) if v is not None])

                # next find the directories in the tiff that match the tags. Note: could be a subset of numeric_tags
                #directories = {k: ifd.directories[k] for k in ifd.directories.keys() & numeric_tags}
                directories = {k: ifd.directories.get(k, None) for k in numeric_tags}

            image_tags.append(directories)

        for ifd in range(len(tiff.ifds)):
            output = TiffDetails.format_output(args.file,
                                            ifd,
                                            tiff.ifds[ifd].offset,
                                            tiff.ifds[ifd].numtags,
                                            tiff.ifds[ifd].nextifd,
                                            list(numeric_tags),
                                            image_tags[ifd],
                                            not args.detail,
                                            args.csv)
            print (output)

    @staticmethod
    def format_output(filename, ifd, offset, numtags, nextifd, req_tags, directories, limit_value=False, csvout=False):
        if csvout:
            out = "{0}\t{1}\t".format(filename, ifd)
            for key in sorted(req_tags):
                if key in directories and directories[key] is not None:
                    out += str(TiffDetails.display_value(directories[key], csvout))
                out += "\t"
        else:
            out = "\n"
            out += "IFD (Offset: " + str(offset) + " | num tags: " + str(numtags) + " | next IFD: " + str(nextifd)\
                   + ")\n"

            for tag, directory in directories.items():
                if directory is not None:
                    out += directory.tostring(limit_value)

                    if tag==34675:
                        profile = IccProfile(directory.value)
                        out += profile.tostring(limit_value)
                else:
                    out += "[{0}]\t[Not Present]".format(tag)
                out += "\n"

        return out

    @staticmethod
    def display_value(directory, csvout=False):
        """Converts Tiff tag values to something more appropriate, as easily allowed"""

        # TYPES
        if directory.type == 2:     # ascii
            return ''.join(chr(i) for i in directory.value[:-1])

        # TAGS
        elif directory.tag == 34675:   # ICC Profile
            profile = IccProfile(directory.value)
            if csvout:
                return profile.header['data_colour_space']
            else:
                out = ""
                for icc_tag, icc_value in profile.header.items:
                    out += "[{0}\t{1}\n".format(icc_tag, icc_value)
                return out

        return directory.value


module = TiffDetails()  # initiate module class when module imported