class IccProfile():
    """Parses an ICC Colour Profile.
       According to spec: all Profile data shall be encoded as big-endian"""

    def __init__(self, bytes):
        self.header = {}
        self.parse_icc(bytes)

    def get_colour_space(self):
        """Returns the data colour space type, or None if not defined"""
        return self.header.get('data_colour_space')

    def tostring(self, limit_value=False):
        out = "\nHEADER\n"
        for k, v in self.header.items():
            out += "  [{0:27}]\t{1:31}\n".format(k, v)

        out += "\nTAGS ({0})\n".format(self.tag_count)
        for tag, (offset, size, value) in self.tags.items():
            if len(value)>100 and limit_value:
                out += "  [{0}]\t{1}\t{2}\t{3}...\n".format(tag, offset, size, value[:100])
            else:
                out += "  [{0}]\t{1}\t{2}\t{3}\n".format(tag, offset, size, value)

        return out

    def parse_icc(self, bytes):
        """Parsers the specified bytes representing an ICC Profile"""

        # ICC profile consists of:
        #  - 128-byte profile header
        #  - profile tag table:
        #  - profile tagged element data (referenced from tag table)
        if bytes is not None:
            self.read_header(bytes)
            self.read_tags(bytes)

    def read_header(self, bytes):
        self.header['profile_size'] = IccProfile.read_int(bytes, 0)
        self.header['preferred_cmm_type'] = IccProfile.read_string(bytes, 4, 4)
        self.header['profile_version_number'] = IccProfile.read_binary_coded_decimal(bytes, 8)
        self.header['profile_device_class'] = IccProfile.read_string(bytes, 12, 4)
        self.header['data_colour_space'] = IccProfile.read_string(bytes, 16, 4)
        self.header['pcs'] = IccProfile.read_string(bytes, 20, 4)
        self.header['creation_datetime'] = IccProfile.read_datetime(bytes, 24)                  # YY-mm-dd HH:mm:ss
        self.header['acsp'] = IccProfile.read_string(bytes, 36, 4)                             # Must = acsp
        self.header['primary_platform_sig'] = IccProfile.read_string(bytes, 40, 4)             # APPL, MSFT, SGI, SUNW, 0
        self.header['profile_flags'] = IccProfile.read_int(bytes, 44)                           # todo: flags
        self.header['device_manufacturer'] = IccProfile.read_string(bytes, 48, 4)
        self.header['device_model'] = IccProfile.read_int(bytes, 52)
        self.header['device_attributes'] = IccProfile.read_int(bytes, 56)                       # todo: flags
        self.header['rendering_intent'] = IccProfile.read_int(bytes, 64)
        self.header['nciexyz_values'] = IccProfile.read_xyznumber(bytes, 68)
        self.header['profile_creator_signature'] = IccProfile.read_string(bytes, 80, 4)
        self.header['profile_id'] = str(bytes[84:99])
        self.header['reserved'] = str(bytes[100:128])

    def read_tags(self, bytes):
        # 4 bytes tag count
        # n x 12 byte tags (4 bytes sig, 4 bytes offset (relative to profile start), 4 bytes size of data element)
        self.tag_count = IccProfile.read_int(bytes, 128)
        self.tags = {}

        for t in range(self.tag_count):
            type = IccProfile.read_string(bytes, 132+(t*12), 4)
            offset = IccProfile.read_int(bytes, 136+(t*12))
            size = IccProfile.read_int(bytes, 140+(t*12))

            read_func = tagtypes.get(type)
            if read_func is not None:
                #read_func = getattr(IccProfile, tag_tuple[0])
                value = read_func(bytes, offset, size)
            else:
                value = bytes[offset: offset+size]
            self.tags[type] = (offset, size, value)

    @staticmethod
    def read_int(bytes, offset, count=1, size=4, byteorder='big'):
        return int.from_bytes(bytes[offset:offset+size], byteorder=byteorder)

    @staticmethod
    def read_string(bytes, offset, count, byteorder='big'):
        return ''.join(map(chr, bytes[offset:offset+count]))

    @staticmethod
    def read_binary_coded_decimal(bytes, start):
        out = "{0}.{1}.{2}".format(bytes[start],
                                   bytes[start+1]>>4,
                                   bytes[start+1]&0x0F)
        return out

    @staticmethod
    def read_datetime(bytes, offset, byteorder='big'):
        out = "{0}-{1}-{2} {3}:{4}:{5}".format(str(int.from_bytes(bytes[offset:offset + 2], byteorder=byteorder)),
                                               str(int.from_bytes(bytes[offset + 2:offset + 4], byteorder=byteorder)),
                                               str(int.from_bytes(bytes[offset + 4:offset + 6], byteorder=byteorder)),
                                               str(int.from_bytes(bytes[offset + 6:offset + 8], byteorder=byteorder)),
                                               str(int.from_bytes(bytes[offset + 8:offset + 10], byteorder=byteorder)),
                                               str(int.from_bytes(bytes[offset + 10:offset + 12], byteorder=byteorder)))
        return out

    @staticmethod
    def read_signature_type(bytes, offset, count):
        assert (IccProfile.read_string(bytes, offset, 4) == 'sig ')
        assert (IccProfile.read_int(bytes, offset + 4) == 0)
        return IccProfile.read_string(bytes, offset+8, 4)

    @staticmethod
    def read_xyztype(bytes, offset, count):
        sig = IccProfile.read_string(bytes, offset, 4)
        assert(IccProfile.read_int(bytes, offset+4) == 0)
        # todo: repeat xyz for remainder of xyztype bytes
        xyz = IccProfile.read_xyznumber(bytes, offset+8)

        return "{0}: {1}".format(sig, xyz)

    @staticmethod
    def read_xyznumber(bytes, offset, byteorder='big'):
        x_i = IccProfile.read_s15Fixed16Number(bytes, offset)
        y_i = IccProfile.read_s15Fixed16Number(bytes, offset+4)
        z_i = IccProfile.read_s15Fixed16Number(bytes, offset+8)

        return "X={0}, Y={1}, Z={2}".format(x_i, y_i, z_i)

    @staticmethod
    def read_trctype(bytes, offset, count):
        # check first 4 bytes, either 'curv' or 'para'
        sig = IccProfile.read_string(bytes, offset, 4)
        if sig=='curv':
            # next 4 bytes 0
            assert (IccProfile.read_int(bytes, offset + 4) == 0)
            n = IccProfile.read_int(bytes, offset+8)
            vals = [IccProfile.read_int(bytes, offset+12+(2*i), size=2) for i in range(n)]
        # todo: para

        return "{0} : count {1} : {2}".format(sig, n, vals)

    @staticmethod
    def read_s15Fixed16Number(bytes, offset):
        conv = lambda x: ((x & 0xffff0000) >> 16) + ((x & 0x0000ffff) / 65536)
        return conv(int.from_bytes(bytes[offset:offset + 4], byteorder='big'))

    @staticmethod
    def read_s15Fixed16ArrayType(bytes, offset, count):
        assert(IccProfile.read_string(bytes, offset, 4) == 'sf32')
        assert(IccProfile.read_int(bytes, offset+4) == 0)
        n = int((count-8)/4)
        return [IccProfile.read_s15Fixed16Number(bytes, offset+8+(i*4)) for i in range(n)]

tagtypes = {
    'chad': (IccProfile.read_s15Fixed16ArrayType),
    'cprt': (IccProfile.read_string),
    'desc': (IccProfile.read_string),
    'dmdd': (IccProfile.read_string),
    'tech': (IccProfile.read_signature_type),
    'vued': (IccProfile.read_string),
    'wtpt': (IccProfile.read_xyztype),
    'bkpt': (IccProfile.read_xyztype),      # private type?
    'rTRC': (IccProfile.read_trctype),
    'gTRC': (IccProfile.read_trctype),
    'bTRC': (IccProfile.read_trctype),
    'rXYZ': (IccProfile.read_xyztype),
    'gXYZ': (IccProfile.read_xyztype),
    'bXYZ': (IccProfile.read_xyztype),
}

if __name__=='__main__':
    import numpy as np
    import sys
    with open(sys.argv[1], 'rb') as file:
        data = np.fromfile(file, dtype="uint8")
        profile = IccProfile(data)
        print(profile.tostring())