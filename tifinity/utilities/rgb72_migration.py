from tifinity.parser.tiff import Tiff
from tifinity.actions.rgb72_to_rgb96 import *
from tifinity.scripts.timing import *

@time_usage
def migrate_tiff(fromfile, to_file):
    tiff = Tiff(fromfile)

    # Convert image data
    rgb72_to_rgb96(tiff)

    # Write new TIFF
    tiff.save_tiff(to_file)


def main():
    migrate_tiff("C:/Data/EAP061/TestConversions/Original/0010.tif",
                 "C:/Data/EAP061/TestConversions/Original/conv_0010_2.tif")


if __name__=='__main__':
    main()
