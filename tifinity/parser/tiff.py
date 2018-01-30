import math
from tifinity.scripts.timing import time_usage

ifdtype = {
    1: 1,  # byte      - 1 byte
    2: 1,  # ascii     - 1 byte
    3: 2,  # short     - 2 bytes
    4: 4,  # long      - 4 bytes
    5: 8,  # rational  - 8 bytes
    6: 1,  # sbyte     - 1 byte
    7: 1,  # undefined - 1 byte
    8: 2,  # sshort    - 2 bytes
    9: 4,  # slong     - 4 bytes
    10: 8,  # srational - 8 bytes
    11: 4,  # float     - 4 bytes
    12: 8  # double    - 8 bytes
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


## TIFF stuff
class Directory:
    def __init__(self, tag, type, count, value):
        self.tag = tag
        self.type = type
        self.count = count
        self.value = value

    def setTagOffset(self, offset):
        self.sot_offset = offset  # start of tag offset

    def tostring(self):
        tagname = "Unknown"
        if self.tag in ifdtag:
            tagname = ifdtag[self.tag]
        return "[{0}]\t{1:31}\t{2:2}\t{3:3}\t{4}".format(self.tag, tagname, self.type, self.count, self.value)


class IFD:
    def __init__(self, offset):
        self.offset = offset
        self.numtags = 0
        self.directories = {}
        self.nextifd = 0
        self.pointerlocation = 0

    def addDirectory(self, dir):
        self.directories[dir.tag] = dir

    def getImageWidth(self):
        return self.directories[256].value[0]

    def getImageHeight(self):
        return self.directories[257].value[0]

    def getBitsPerSample(self):
        return self.directories[258].value

    def setBitsPerSample(self, bps=[8, 8, 8]):
        bps_bytes = [x.to_bytes(2, byteorder='little') for x in bps]
        self.directories[inv_ifdtag["BitsPerSample"]].value = bps_bytes

    # def getCompression(self):
    #     return self.directories[259].value
    #
    # def getPhotometrics(self):
    #     return self.directories[262].value

    def getRowsPerStrip(self):
        '''Returns the number of pixel rows per strip in this IFD's image'''
        # TODO: Default number of rows per strip
        return self.directories[278].value[0]

    def setRowsPerStrip(self, rows):
        self.directories[inv_ifdtag["RowsPerStrip"]].value = rows

    def getStripsPerImage(self):
        '''Returns the number of Strips for this IFD's image'''
        rps = self.getRowsPerStrip()
        return math.floor((self.getImageHeight() + rps - 1) / rps)

    def getStrips(self):
        '''Returns a list of tuples about each Strip in this IFD's image(strip_offset, strip_byte_count)'''
        return list(zip(self.directories[273].value, self.directories[279].value))

    def setStripOffsets(self, offsets):
        '''Sets the strip offsets for this IFD's image'''
        assert (len(offsets) == self.getTagCount(inv_ifdtag["StripOffsets"]))
        # self.directories[inv_ifdtag["StripOffsets"]].setTagOffset
        # TODO: Finish setStripOffsets (if necessary)

    def getStripOffsets(self):
        '''Returns a list of offsets for each Strip in this IFD's image'''
        return self.directories[273].value

    def setStripByteCounts(self, counts):
        # TODO: store counts in byte size relating to tag type
        # counts_bytes = [x.to_bytes(4, byteorder='little') for x in counts]
        self.directories[inv_ifdtag["StripByteCounts"]].value = counts

    def getBytesPerPixel(self):
        return sum([int(int.from_bytes(x, byteorder='little') / 8) for x in self.directories[258].value])

    def getTagType(self, tag):
        return self.directories[tag].type

    def getTagCount(self, tag):
        return self.directories[tag].count

    def setTagCount(self, tag, count):
        self.directories[tag].count = count

    def getTagValue(self, tag):
        return self.directories[tag].value

    def getTagOffset(self, tag):
        return self.directories[tag].sot_offset

    # def setTagValue(self, tag, value):
    #     self.directories[tag].sot_offset = value

    def printIFD(self):
        print("IFD (Offset: " + str(self.offset) + " | num tags: " + str(self.numtags) + " | next IFD: " + str(
            self.nextifd) + ")")
        for tag, dir in self.directories.items():
            print(dir.tostring())
        # print ("  Width:             "+str(self.getImageWidth()))
        # print ("  Height:            "+str(self.getImageHeight()))
        # print ("  Bits Per Sample:   "+str(self.getBitsPerSample()))
        # print ("  Compression:       "+str(self.getCompression()))
        # print ("  Photometrics:      "+str(self.getPhotometrics()))
        # print ("  StripOffsets:      "+str(self.getStripOffsets()))
        # print ("  Rows Per Strip:    "+str(self.getRowsPerStrip()))
        # print ("  Strip Byte Counts: "+str(self.getStripByteCount()))


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
    def __init__(self, tif_file):
        self.tif_file = tif_file
        self.byteOrder = 'big'
        self.ifds = []
        self.img_data = None
        self.row_data = []

    def readTiff(self):
        nextifd_offset = self.readHeader()
        # read in each IFD and image data
        while nextifd_offset != 0:
            ifd = self.readIFD(nextifd_offset)
            self.ifds.append(ifd)

            self.readImage(ifd)

            nextifd_offset = ifd.nextifd

    def writeTiff(self, to_file):
        self.to_file = to_file
        self.writeHeader(8)  # first IFD always at 0x08

        for ifd in self.ifds:
            # self.calculateIFDSpace(ifd)     # Readjusts counts because of changes to image data
            endpos = self.writeIFD(ifd)
            self.writeImage(ifd, endpos)

    # Do this if change stuff having read the TIFF, e.g. migrated the image data. Otherwise
    # assume all is the same size - even if the offsets have changed.
    def calculateIFDSpace(self, ifd):
        strips_per_image = ifd.getStripsPerImage()
        ifd.setTagCount(inv_ifdtag["StripOffsets"], strips_per_image)
        ifd.setTagCount(inv_ifdtag["StripByteCounts"], strips_per_image)

    def writeHeader(self, ifd_offset):
        # byte order
        byteo = 'II'
        if self.byteOrder != 'little':
            byteo = 'MM'
        self._writeBytes(byteo.encode())

        # Magic number
        self._writeInt(42, 2)

        # IFD offset
        self._writeInt(ifd_offset, 4)

    def writeIFD(self, ifd):
        # Writes: num directories, directories, offset values, space for next ifd

        # first calculate end of IFD offset where directory values can be written
        # end = curpos + (num directories) + (n directories) + offset to nextIFD
        end = self.to_file.tell() + 2 + (ifd.numtags * 12) + 4

        self._writeInt(ifd.numtags, 2)

        # assumes sorted
        for tag, dir in ifd.directories.items():
            dir.setTagOffset(self.to_file.tell())  # set start of tag offset for later
            self._writeInt(dir.tag, 2)
            self._writeInt(dir.type, 2)
            self._writeInt(dir.count, 4)
            end = self._writeValue(dir, end)

        self._writeInt(ifd.nextifd, 4)  # pointer to next IFD, or 0x00000000

        return end

    def _writeValue(self, dir, endpos):
        # if count=1 -> value=value; if count>1 -> value=list location

        if (dir.count * ifdtype[dir.type] > 4):
            self._writeInt(endpos, 4)  # write the offset of the binary data
            curpos = self.to_file.tell()
            self.to_file.seek(endpos)  # jump to that offset
            # self._writeBytes(bytes(dir.value))
            self._writeBytes(b''.join(dir.value))
            endpos = self.to_file.tell()
            self.to_file.seek(curpos)
        elif ((dir.count > 1) and
              (ifdtype[dir.type] * dir.count == 4)):  # count>1 but still fits in 4 bytes
            self._writeBytes(b''.join(dir.value))  # dir.value = [bytes] so needs joining together
        else:
            self._writeInt(dir.value[0], 4)

        # if dir.count == 1:
        #     self._writeInt(dir.value[0], 4)
        # elif ((dir.count > 1) and
        #       (ifdtype[dir.type] * dir.count == 4)): # count>1 but still fits in 4 bytes
        #     self._writeBytes(b''.join(dir.value))              # dir.value = [bytes] so needs joining together
        # else:                                        # more than 4 bytes in actual value
        #     self._writeInt(endpos, 4)                # write the offset of the binary data
        #     curpos = self.to_file.tell()
        #     self.to_file.seek(endpos)                    # jump to that offset
        #     #self._writeBytes(bytes(dir.value))
        #     self._writeBytes(b''.join(dir.value))
        #     endpos = self.to_file.tell()
        #     self.to_file.seek(curpos)
        return endpos

    def writeImage(self, ifd, endpos):
        bytes_per_row = ifd.getImageWidth() * ifd.getBytesPerPixel()
        strips_per_image = ifd.getStripsPerImage()
        bytes_per_strip = ifd.getRowsPerStrip() * bytes_per_row

        bytes_remaining = len(self.img_data)
        bytes_to_write = bytes_per_strip

        strips = []  # [(strip_offset, strip_byte_count)]

        self.to_file.seek(endpos)  # jump to the end for writing image data

        startpos = 0
        for s in range(strips_per_image):
            strip_pos = self.to_file.tell()

            if (bytes_remaining < bytes_to_write):
                bytes_to_write = bytes_remaining

            bytes_written = self._writeBytes(self.img_data[startpos:startpos + bytes_to_write])
            bytes_remaining -= bytes_written
            startpos += bytes_written
            strips.append((strip_pos, bytes_written))

        # now set stripoffset
        offsets = [x for (x, y) in strips]  # the actual offsets
        bytes = [y for (x, y) in strips]  # actual number bytes per strip

        str_offset_tag = inv_ifdtag["StripOffsets"]
        self.to_file.seek(ifd.getTagOffset(str_offset_tag) + 8)  # jump to directory.value
        if ifdtype[ifd.getTagType(str_offset_tag)] * ifd.getTagCount(str_offset_tag) > 4:
            # value to write is larger than 4 bytes, so jump to the offset value array
            self.to_file.seek(ifd.getTagValue(str_offset_tag))

        # now write the offsets
        for o in offsets:
            self._writeInt(o, ifd.getTagType(str_offset_tag))

        str_bytes_tag = inv_ifdtag["StripByteCounts"]
        self.to_file.seek(ifd.getTagOffset(str_bytes_tag) + 8)  # jump to directory.value
        if ifdtype[ifd.getTagType(str_bytes_tag)] * ifd.getTagCount(str_bytes_tag) > 4:
            # value to write is larger than 4 bytes, so jump to the offset value array
            self.to_file.seek(ifd.getTagValue(str_bytes_tag))

        # now write the offsets
        for o in bytes:
            self._writeInt(o, ifd.getTagType(str_bytes_tag))

    def _readBytes(self, numbytes):
        return self.tif_file.read(numbytes)

    def _readInt(self, numbytes):
        b = self.tif_file.read(numbytes)
        return int.from_bytes(b, byteorder=self.byteOrder)

    def _writeBytes(self, bytestowrite):
        return self.to_file.write(bytestowrite)

    def _writeInt(self, number, numbytes=4):
        b = number.to_bytes(numbytes, byteorder=self.byteOrder)
        self.to_file.write(b)

    def _readValue(self, type, count):
        # TODO: Fix for rationals
        retval = []
        value = self._readInt(4)  # count=1 -> value=value; count>1 -> value=list location

        if (count * ifdtype[type] > 4):
            # value is pointer
            curpos = self.tif_file.tell()
            self.tif_file.seek(value)  # jump to offset, read and return
            # retval.extend(self._readBytes((ifdtype[type] * count)))
            for i in range(count):
                retval.append(self._readBytes(ifdtype[type]))  # read appropriate number of bytes
            self.tif_file.seek(curpos)
        elif ((count > 1) and
              (ifdtype[type] * count == 4)):  # count>1 but still fits in 4 bytes
            retval.extend(self._readBytes((ifdtype[type] * count)))
        else:
            # count == 1 and value fits within 4 bytes
            retval.append(value)

        # if count == 1:
        #     retval.append(value)
        # elif ((count > 1) and
        #       (ifdtype[type] * count == 4)):        # count>1 but still fits in 4 bytes
        #     retval.extend(self._readBytes((ifdtype[type] * count)))
        # else:                                       # more than 4 bytes in actual value
        #     curpos = self.tif_file.tell()
        #     self.tif_file.seek(value)                    # jump to offset, read and return
        #     #retval.extend(self._readBytes((ifdtype[type] * count)))
        #     for i in range(count):
        #         retval.append(self._readBytes(ifdtype[type]))   # read appropriate number of bytes
        #     self.tif_file.seek(curpos)
        return retval

    def readHeader(self):
        # Byte order
        h = self.tif_file.read(2)
        if h != 'II':
            self.byteOrder = 'little'
        print("ByteOrder: " + self.byteOrder)

        # Magic number
        self.magic = self._readInt(2)
        print("Magic: " + str(self.magic))
        assert (self.magic == 42)

        # IFD offset
        # self.ifds[0] = IFD(self._readInt(4))
        return self._readInt(4)  # returns offset to first IFD

    def readIFD(self, ifd_offset):
        # go through IFD
        ifd = IFD(ifd_offset)

        self.tif_file.seek(ifd.offset, 0)
        ifd.numtags = self._readInt(2)

        for i in range(ifd.numtags):
            # read IFD bytes
            tag = self._readInt(2)
            type = self._readInt(2)
            count = self._readInt(4)
            value = self._readValue(type, count)
            # add directory
            ifd.addDirectory(Directory(tag, type, count, value))

        # finally get the next IFD offset
        ifd.nextifd = self._readInt(4)

        # return the IFD
        return ifd

    @time_usage
    def readImage(self, ifd):
        self.img_data = b''
        bytes_per_row = ifd.getImageWidth() * ifd.getBytesPerPixel()
        strips = ifd.getStrips()  # [(strip_offset, strip_byte_count)]
        for strip in strips:
            self.tif_file.seek(strip[0])  # jump to offset
            # read max number of bytes for range
            bytes_left = strip[1]

            # TODO: Account for not enough bytes left in file
            while bytes_left > 0:
                self.img_data += self.tif_file.read(bytes_per_row)
                bytes_left -= bytes_per_row

    # def readImageRows(self, ifd_no):
    #     self.row_data = []
    #
    #     bytes_per_row = self.ifds[ifd_no].imageWidth * int(sum(self.ifds[ifd_no].bps) / 8)
    #
    #     numStrips = len(self.ifds[ifd_no].stripoffset)
    #     for s in range(numStrips):
    #         self.tif_file.seek(self.ifds[ifd_no].stripoffset[s])
    #
    #         # read max number of bytes for range
    #         bytes_left = self.ifds[ifd_no].stripbytecount[s]
    #
    #         while bytes_left > 0:
    #             self.row_data += self.tif_file.read(bytes_per_row)
    #             bytes_left -= bytes_per_row
