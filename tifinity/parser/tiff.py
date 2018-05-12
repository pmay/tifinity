import numpy as np
import math
from struct import unpack_from

from tifinity.parser.errors import InvalidTiffError

ifdtype = {
    1: (1, "read_bytes", "insert_bytes"),          # byte      - 1 byte
    2: (1, "read_bytes", "insert_bytes"),          # ascii     - 1 byte
    3: (2, "read_shorts", "insert_shorts"),        # short     - 2 bytes
    4: (4, "read_ints", "insert_ints"),            # long      - 4 bytes
    5: (8, "read_rationals", "insert_rationals"),  # rational  - 8 bytes
    6: (1, "read", "insert_bytes"),                # sbyte     - 1 byte
    7: (1, "read_bytes", "insert_bytes"),          # undefined - 1 byte
    8: (2, "read_shorts", "insert_shorts"),        # sshort    - 2 bytes
    9: (4, "read_ints", "insert_ints"),            # slong     - 4 bytes
    10: (8, "read_rationals", "insert_rationals"), # srational - 8 bytes
    11: (4, "read_floats", "insert_floats"),       # float     - 4 bytes
    12: (8, "read_doubles", "insert_doubles")      # double    - 8 bytes
}

ifdtag = {
    254: "NewSubfileType",
    255: "SubfileType",
    256: "ImageWidth",
    257: "ImageLength",
    258: "BitsPerSample",
    259: "Compression",
    262: "PhotometricInterpretation",
    263: "Thresholding",
    264: "CellWidth",
    265: "CellLength",
    266: "FillOrder",
    269: "DocumentName",  # ext; TIFF 6.0 Section 12
    270: "ImageDescription",
    271: "Make",
    272: "Model",
    273: "StripOffsets",
    274: "Orientation",
    277: "SamplesPerPixel",
    278: "RowsPerStrip",
    279: "StripByteCounts",
    280: "MinSampleValue",
    281: "MaxSampleValue",
    282: "XResolution",
    283: "YResolution",
    284: "PlanarConfiguration",
    285: "PageName",  # ext
    288: "FreeOffsets",
    289: "FreeByteCounts",
    290: "GrayResponseUnit",
    291: "GrayResponseCurve",
    296: "ResolutionUnit",
    297: "PageNumber",  # ext
    305: "Software",
    306: "DateTime",
    315: "Artist",
    316: "HostComputer",
    317: "Predictor",  # ext; TIFF 6.0 Section 14
    318: "WhitePoint",  # ext; TIFF 6.0 Section 20
    319: "PrimaryChromaticities",  # ext; TIFF 6.0 Section 20
    320: "ColorMap",
    338: "ExtraSamples",
    339: "SampleFormat",  # ext; TIFF 6.0 Section 19
    33432: "Copyright",
    -1: "UNKNOWN"
}

inv_ifdtag = {v: k for k, v in ifdtag.items()}


# TIFF stuff
class Directory:
    def __init__(self, tag, ttype, count, value):
        self.tag = tag
        self.type = ttype
        self.count = count
        self.value = value
        self.sot_offset = 0

    def set_tag_offset(self, offset):
        self.sot_offset = offset  # start of tag offset

    def tostring(self):
        tagname = "Unknown"
        if self.tag in ifdtag:
            tagname = ifdtag[self.tag]
        return "[{0}]\t{1:31}\t{2:2}\t{3:6}\t{4}".format(self.tag, tagname, self.type, self.count, self.value)


class IFD:
    def __init__(self, offset):
        self.offset = offset
        self.numtags = 0
        self.directories = {}
        self.nextifd = 0
        self.pointerlocation = 0
        self.img_data = None
        self.ifd_data = None

    def add_directory(self, directory):
        self.directories[directory.tag] = directory

    def get_image_width(self):
        return self.directories[256].value[0]

    def get_image_height(self):
        return self.directories[257].value[0]

    def get_bits_per_sample(self):
        return self.directories[258].value

    def set_bits_per_sample(self, bps=None):
        if bps is None:
            bps = [8, 8, 8]
        # bps_bytes = [x.to_bytes(2, byteorder='little') for x in bps]
        self.directories[inv_ifdtag["BitsPerSample"]].value = bps

    # def getCompression(self):
    #     return self.directories[259].value
    #
    # def getPhotometrics(self):
    #     return self.directories[262].value

    def get_rows_per_strip(self):
        """Returns the number of pixel rows per strip in this IFD's image"""
        # TODO: Default number of rows per strip
        return self.directories[inv_ifdtag["RowsPerStrip"]].value[0]

    def set_rows_per_strip(self, rows):
        self.directories[inv_ifdtag["RowsPerStrip"]].value = rows

    def get_number_strips(self):
        """Returns the number of Strips for this IFD's image"""
        rps = self.get_rows_per_strip()
        return math.floor((self.get_image_height() + rps - 1) / rps)

    def get_strips(self):
        """Returns a list of tuples about each Strip in this IFD's image(strip_offset, strip_byte_count)"""
        return list(zip(self.directories[273].value, self.directories[279].value))

    def set_strip_offsets(self, offsets):
        """Sets the strip offsets for this IFD's image"""
        assert (len(offsets) == self.get_tag_count(inv_ifdtag["StripOffsets"]))
        # self.directories[inv_ifdtag["StripOffsets"]].setTagOffset
        # TODO: Finish setStripOffsets (if necessary)

    def get_strip_offsets(self):
        """Returns a list of offsets for each Strip in this IFD's image"""
        return self.directories[273].value

    def set_strip_byte_counts(self, counts):
        # TODO: store counts in byte size relating to tag type
        # counts_bytes = [x.to_bytes(4, byteorder='little') for x in counts]
        self.directories[inv_ifdtag["StripByteCounts"]].value = counts

    def get_bytes_per_pixel(self):
        return sum([int(x / 8) for x in self.directories[258].value])

    def get_tag_type(self, tag):
        return self.directories[tag].type

    def get_tag_type_size(self, tag):
        if not isinstance(tag, int):
            tag = inv_ifdtag[tag]
        return ifdtype[self.directories[tag].type][0]

    def get_tag_count(self, tag):
        return self.directories[tag].count

    def set_tag_count(self, tag, count):
        self.directories[tag].count = count

    def get_tag_value_by_name(self, tagname):
        """Returns a tag's value from the IFD, accessed via the tag name itself."""
        return self.directories[inv_ifdtag[tagname]].value

    def get_tag_value(self, tag):
        return self.directories[tag].value

    def get_tag_offset(self, tag):
        return self.directories[tag].sot_offset

    # def setTagValue(self, tag, value):
    #     self.directories[tag].sot_offset = value

    def print_ifd(self):
        print("IFD (Offset: " + str(self.offset) + " | num tags: " + str(self.numtags) + " | next IFD: " + str(
            self.nextifd) + ")")
        for tag, directory in self.directories.items():
            print(directory.tostring())


# Can use 'r+b' mode to overwrite bytes at the current location
#
# TIFF:
#   - header
#      - endianness, 42, IFD0 pointer
#  [- IFDn
#      - num tags
#      - tags
#        [- tag type count value]+
#      - next IFD pointer
#   - Offset values
#   - Image data]+
#   - 0000

# Pointers:
#   - Header -> IFD0
#   - IFD:
#      - Tag Value(s) -> actual value [for arrays larger than 4 bytes]
#      - Next IFD

class Tiff:
    def __init__(self, filename: str):
        """Creates a new Tiff object from the specified Tiff file"""
        self.tif_file = None
        self.byteOrder = 'big'
        self.magic = None
        self.ifds = []

        if filename is not None:
            self.tif_file = TiffFileHandler(filename)
            self.load_tiff()

    def raw_data(self):
        """Returns the numpy array for the entire file"""
        return self.tif_file.raw_data()

    def load_tiff(self):
        """Loads this TIFF into an internal data structure, ready for maniupulation"""

        try:
            # Byte order
            h = bytes(self.tif_file.read(2))
            self.byteOrder = {b'II': 'little', b'MM': 'big'}[h]
            assert (self.byteOrder == 'little' or self.byteOrder == 'big')

            # Magic number
            self.magic = self.tif_file.read_int(2)
            assert (self.magic == 42)
        except (KeyError, AssertionError):
            raise InvalidTiffError("Incorrect header")

        # IFD offset
        nextifd_offset = self.tif_file.read_int(4)  # returns offset to first IFD

        # read in each IFD and image data
        while nextifd_offset != 0:
            ifd = self.read_ifd(nextifd_offset)
            self.ifds.append(ifd)
            self.read_image(ifd)
            nextifd_offset = ifd.nextifd

    def save_tiff(self, to_file=None):
        """Saves the TIFF represented by the internal data structure into the specified file"""
        self.tif_file.clear()   # Empty the array first

        # Header
        byteo = 'II'
        if self.byteOrder != 'little':
            byteo = 'MM'
        self.tif_file.insert_bytes(list(byteo.encode()))    # byte order
        self.tif_file.insert_int(42, 2)                     # Magic number
        self.tif_file.insert_int(8, 4)                      # first IFD always at 0x08

        for ifd in self.ifds:
            # self.calculateIFDSpace(ifd)     # Readjusts counts because of changes to image data
            endpos = self.save_ifd(ifd)
            self.save_image(ifd, endpos)

        self.tif_file.write(to_file)            # lastly, write to file

    # # Do this if change stuff having read the TIFF, e.g. migrated the image data. Otherwise
    # # assume all is the same size - even if the offsets have changed.
    # def calculate_ifd_space(self, ifd):
    #     strips_per_image = ifd.get_strips_per_image()
    #     ifd.set_tag_count(inv_ifdtag["StripOffsets"], strips_per_image)
    #     ifd.set_tag_count(inv_ifdtag["StripByteCounts"], strips_per_image)

    def read_ifd(self, ifd_offset):
        # go through IFD
        ifd = IFD(ifd_offset)

        self.tif_file.seek(ifd.offset)
        ifd.numtags = self.tif_file.read_int(2)

        # save the raw data in the IFD
        ifd.ifd_data = self.tif_file.read(size=(2+(ifd.numtags*12)+4), location=ifd_offset)

        for i in range(ifd.numtags):
            # read IFD bytes
            tag = self.tif_file.read_int(2)
            tag_type = self.tif_file.read_int(2)
            count = self.tif_file.read_int(4)

            value_loc = self.tif_file.tell()   # current location in tiff array

            # TIFF v6 spec, pg 16:
            # "Warning: It is possible that other TIFF field types will be added in the future.
            #  Readers should skip over fields containing an unexpected field type."
            ifdtype_tuple = ifdtype.get(tag_type)

            if ifdtype_tuple is not None:
                # found a tag type within TIFF v6 specified ranges
                if count * ifdtype_tuple[0] > 4:       # next 4 bytes are a pointer to the value's location
                    value_loc = self.tif_file.read_int(4)

                read_func = getattr(self.tif_file, ifdtype_tuple[1])

                value = read_func(count=count, location=value_loc)
                # TODO: Need to handle case where <4 bytes are read

                if count * ifdtype_tuple[0] <= 4:
                    self.tif_file.offset(4)
            else:
                # tag type outside TIFF v6 specified ranges
                # skip next 4 bytes and set value to "Unknown tag type; value unknown"
                self.tif_file.offset(4)
                value = "Unknown tag type; value unknown"

            # add directory
            ifd.add_directory(Directory(tag, tag_type, count, value))

        # finally get the next IFD offset
        ifd.nextifd = self.tif_file.read_int(4)

        # return the IFD
        return ifd

    def save_ifd(self, ifd):
        # Writes: num directories, directories, offset values, space for next ifd

        start_of_ifd = self.tif_file.tell()

        # first calculate end of IFD offset where directory values can be written
        # end = curpos + (num directories) + (n directories) + offset to nextIFD
        num_bytes = 2 + (ifd.numtags * 12) + 4
        end_of_ifd = start_of_ifd + num_bytes                        # location after IFD for IFD values
        self.tif_file.insert_bytes(np.zeros((num_bytes,), dtype='uint8'))  # write empty IFD

        self.tif_file.seek(start_of_ifd)
        self.tif_file.insert_int(ifd.numtags, size=2, overwrite=True)

        # assumes sorted tags
        for tag, directory in ifd.directories.items():
            directory.set_tag_offset(self.tif_file.tell())            # set start of tag offset for later
            self.tif_file.insert_int(directory.tag, size=2, overwrite=True)
            self.tif_file.insert_int(directory.type, size=2, overwrite=True)
            self.tif_file.insert_int(directory.count, size=4, overwrite=True)

            write_func = getattr(self.tif_file, ifdtype[directory.type][2])

            overwrite_value = True
            value_loc = self.tif_file.tell()

            if directory.count * ifdtype[directory.type][0] > 4:       # next 4 bytes are a pointer to the value
                self.tif_file.insert_int(end_of_ifd, size=4, overwrite=True)   # so write pointer then jump to location
                value_loc = end_of_ifd
                overwrite_value = False

            num_written = write_func(directory.value, location=value_loc, overwrite=overwrite_value)

            if directory.count * ifdtype[directory.type][0] > 4:
                end_of_ifd += num_written
            else:
                self.tif_file.offset(4)             # _offset is not updated if location set in write_func

        self.tif_file.insert_int(ifd.nextifd, size=4, overwrite=True)  # pointer to next IFD, or 0x00000000

        return end_of_ifd

    def read_image(self, ifd):
        """Reads the full image data for the specified IFD into a numpy array"""
        ifd.img_data = np.array([], dtype='uint8')
        strips = ifd.get_strips()  # [(strip_offset, strip_byte_count)]
        for strip in strips:
            ifd.img_data = np.append(ifd.img_data, self.tif_file.read(size=strip[1], location=strip[0]))

    def save_image(self, ifd, endpos):
        """Inserts the specified IFD's image data into the tiff numpy array at the specified end position."""
        # Assumes:
        #  1. StripOffsets has count set appropriately, however values are not set/correct and need updating
        #  2. StripByteCounts has count and values set appropriately.
        #  3. StripOffsets or StripByteCounts count value is correct for the number of strips per image (at least for
        #     chunky planar configuration (RGBRGBRGB...))

        num_strips = ifd.get_number_strips()

        strip_byte_counts = [y for (x, y) in ifd.get_strips()]
        strip_offsets = []

        self.tif_file.seek(endpos)  # jump to the end for writing image data

        start_pos = 0
        for num_bytes in strip_byte_counts:
            strip_offsets.append(self.tif_file.tell())                              # record position of strip start
            self.tif_file.insert_bytes(ifd.img_data[start_pos:start_pos + num_bytes])
            start_pos += num_bytes

        # now set strip offsets in IFD
        strip_offset_tag = inv_ifdtag["StripOffsets"]
        strip_offset_value_location = ifd.get_tag_offset(strip_offset_tag) + 8

        if ifdtype[ifd.get_tag_type(strip_offset_tag)][0] * num_strips > 4:
            # value to write is larger than 4 bytes, so get the offset for the value array
            strip_offset_value_location = ifd.get_tag_value(strip_offset_tag)

        # now write the offsets
        tag_type_size = ifd.get_tag_type_size("StripOffsets")

        self.tif_file.insert_ints(strip_offsets, tag_type_size, location=strip_offset_value_location, overwrite=True)


class TiffFileHandler(object):
    """Handler which imports a TIFF file into a numpy array for reading and/or writing.
       Writing creates a copy of the file."""
    def __init__(self, filename: str) -> object:
        self._byteorder = 'little'
        self._filename = filename
        self._offset = 0

        with open(filename, 'rb') as in_file:
            self._tiff = np.fromfile(in_file, dtype="uint8")

    def raw_data(self):
        return self._tiff

    def set_byte_order(self, byteorder='little'):
        """Sets the byte order to be used for subsequent reads"""
        self._byteorder = byteorder

    def clear(self):
        """Empties the current numpy array for this Tiff"""
        self._tiff = np.array([], dtype="uint8")
        self._offset = 0

    def read(self, size=1, count=1, location=None):
        """Reads the next 'size' bytes at the specified location, or the current offset if no location is supplied.

           If location is specified, this read will not update the current offset"""
        if self._tiff is not None:
            off = self._offset
            if location is not None:
                off = location
            b = self._tiff[off:off+size]
            if location is None:
                self._offset += size
            return b

    def read_bytes(self, count=1, location=None):
        """Reads 'count' bytes from the specified location, or the current offset if no location is supplied."""
        return_vals = []
        if self._tiff is not None:
            off = self._offset
            if location is not None:
                off = location
            return_vals = list(self._tiff[off:off+count])
            if location is None:
                self._offset += count
            return return_vals

    def insert_bytes(self, bytes_to_write, location=None, overwrite=False):
        """Inserts or overwrites the values at the specified location, or the current offset if no location
           is specified."""
        num_bytes = len(bytes_to_write)

        off = self._offset
        if location is not None:
            off = location
        if overwrite:
            self._tiff[off:off + num_bytes] = bytes_to_write
        else:
            self._tiff = np.insert(self._tiff, off, bytes_to_write)
        if location is None:
            self._offset += num_bytes

        return num_bytes

    def read_floats(self, count=1, location=None):
        """Reads the next 'count' lots of 4 bytes at the specified location, or the current offset if no location is supplied,
            and interprets these bytes as a IEEE 754 float.

            If location is specified, this read will not update the current offset"""
        return_vals = []
        byteorder = {'little':'<f', 'big':'>f'}[self._byteorder]
        if self._tiff is not None:
            off = self._offset
            if location is not None:
                off = location
            for c in range(count):
                return_vals.append(unpack_from(byteorder, self._tiff[off:off+4])[0])
                off += 4# size
            if location is None:
                self._offset += (count * 4) #size)
            return return_vals

    def read_doubles(self, count=1, location=None):
        """Reads the next 'count' lots of 8 bytes at the specified location, or the current offset if no location is supplied,
            and interprets these bytes as a IEEE 754 double.

            If location is specified, this read will not update the current offset"""
        return_vals = []
        byteorder = {'little': '<d', 'big': '>d'}[self._byteorder]
        if self._tiff is not None:
            off = self._offset
            if location is not None:
                off = location
            for c in range(count):
                return_vals.append(unpack_from(byteorder, self._tiff[off:off + 8])[0])
                off += 8  # size
            if location is None:
                self._offset += (count * 8)  # size)
            return return_vals

    def insert_floats(self, numbers, location=None, overwrite=False):
        """Inserts the specified IEEE 754 floats into the tiff array at the specified location.
           If overwrite is True, the bytes overwrite those at the write location; if False, the bytes are
           inserted at the write location"""
        pass
        # def flatten(l): return [x for sublist in l for x in sublist]
        # def tobytes(x): return list(x.to_bytes(size, byteorder=self._byteorder))
        #
        # bytes_to_write = flatten([tobytes(x) for x in numbers])
        # return self.insert_bytes(bytes_to_write, location, overwrite)

    def read_int(self, size=4, location=None):
        """Reads a single int of 'size' bytes at the specified location, or the current offset if no location is
           supplied."""
        return self.read_ints(size=size, location=location)[0]

    def read_ints(self, size=4, count=1, location=None):
        """Reads the next 'count' 'size' bytes at the specified location, or the current offset if no location is supplied,
           and interprets these bytes as an integer.

           If location is specified, this read will not update the current offset"""
        return_vals = []
        if self._tiff is not None:
            off = self._offset
            if location is not None:
                off = location
            for c in range(count):
                return_vals.append(int.from_bytes(self._tiff[off:off+size], byteorder=self._byteorder))
                off += size
            if location is None:
                self._offset += (count * size)
            return return_vals

    def insert_int(self, value, size=4, location=None, overwrite=False):
        """Inserts the specified value encoded in size bytes into the tiff array at the specified location.
           If overwrite is True, the bytes overwrite those at the write location; if False, the bytes are
           inserted at the write location"""
        self.insert_ints([value], size=size, location=location, overwrite=overwrite)

    def insert_ints(self, numbers, size=4, location=None, overwrite=False):
        """Inserts the specified number encoded in size bytes into the tiff array at the specified location.
           If overwrite is True, the bytes overwrite those at the write location; if False, the bytes are
           inserted at the write location"""
        def flatten(l): return [x for sublist in l for x in sublist]
        def tobytes(x): return list(x.to_bytes(size, byteorder=self._byteorder))

        bytes_to_write = flatten([tobytes(x) for x in numbers])
        return self.insert_bytes(bytes_to_write, location, overwrite)

    def read_rationals(self, count=1, location=None):
        """Reads in a TIFF Rational data type (2 4-byte integers)"""
        return_vals = []
        if self._tiff is not None:
            off = self._offset
            if location is not None:
                off = location
            for c in range(count):
                num = int.from_bytes(self._tiff[off:off + 4], byteorder=self._byteorder)
                denom = int.from_bytes(self._tiff[off+4:off + 8], byteorder=self._byteorder)
                return_vals.append((num, denom))
                off += 8
            if location is None:
                self._offset += (count * 8)
            return return_vals

    def insert_rationals(self, values, location=None, overwrite=False):
        """Inserts or overwrites the specified rational values at the specified location, or the current offset
           if no location is specified."""
        def flatten(l): return [x for sublist in l for x in sublist]
        def tobytes(x): return list(x.to_bytes(4, byteorder=self._byteorder))

        bytes_to_write = flatten([tobytes(n) + tobytes(d) for (n, d) in values])
        num_bytes = len(bytes_to_write)

        off = self._offset
        if location is not None:
            off = location
        if overwrite:
            self._tiff[off:off + num_bytes] = bytes_to_write
        else:
            self._tiff = np.insert(self._tiff, off, bytes_to_write)
        if location is None:
            self._offset += num_bytes

        return num_bytes

    def read_shorts(self, count=1, location=None):
        """Reads in a TIFF Short data type (2-byte integer)"""
        return self.read_ints(size=2, count=count, location=location)

    def insert_shorts(self, numbers, location=None, overwrite=False):
        """Inserts or overwrites the specified short numbers at the specified location, or the current offset if
           no location is specified."""
        return self.insert_ints(numbers, 2, location, overwrite)

    def write(self, tofile=None):
        """Writes the current np byte array to the specified file, or a copy of this TIFF file (if no file is
           specified)."""
        if tofile is None:
            tofile = self._filename[:-4]+"_tifinity.tiff"

        with open(tofile, 'wb') as out_file:
            self._tiff.tofile(out_file)         # numpy.tofile()

    def seek(self, offset, location=0):
        """Sets the current offset relative to the specified location"""
        if (0 <= location <= len(self._tiff)) and (0 <= location+offset <= len(self._tiff)):
            self._offset = location+offset

    def offset(self, offset):
        """Sets the offset relative to the current offset"""
        self._offset += offset

    def tell(self):
        """Returns the current offset"""
        return self._offset
