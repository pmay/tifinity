class IccProfile():

    def __init__(self, bytes):
        self.header = {}

        self.parse_icc(bytes)


    def get_colour_space(self):
        """Returns the colour space type, or None if not defined"""
        return self.header.get('data_colour_space')

    def tostring(self):
        out = "\n"
        for k, v in self.header.items():
            out += "[{0:27}]\t{1:31}\n".format(k, v)
        return out

    def parse_icc(self, bytes):
        """Parsers the specified bytes representing an ICC Profile"""

        # ICC profile consists of:
        #  - 128-byte profile header
        #  - profile tag table:
        #  - profile tagged element data (referenced from tag table)
        if bytes is not None:
            self.read_header(bytes)


    def read_header(self, bytes):
        self.header['profile_size'] = IccProfile.read_int(bytes, 0)
        self.header['preferred_cmm_type'] = IccProfile.read_int(bytes, 4)
        self.header['profile_version_number'] = IccProfile.read_binary_coded_decimal(bytes, 8)
        self.header['profile_device_class'] = IccProfile.read_string(bytes, 12, 16)
        self.header['data_colour_space'] = IccProfile.read_string(bytes, 16, 20)
        self.header['pcs'] = IccProfile.read_string(bytes, 20, 24)
        self.header['creation_datetime'] = IccProfile.read_datetime(bytes, 24, 35)
        self.header['acsp'] = IccProfile.read_int(bytes, 36)
        self.header['primary_platform_sig'] = IccProfile.read_int(bytes, 40)
        self.header['profile_flags'] = IccProfile.read_int(bytes, 44)
        self.header['device_manufacturer'] = IccProfile.read_int(bytes, 48)
        self.header['device_model'] = IccProfile.read_int(bytes, 52)
        self.header['device_attributes'] = IccProfile.read_int(bytes, 56)
        self.header['rendering_intent'] = IccProfile.read_int(bytes, 64)
        #self.header['nciexyz_values'] =
        self.header['profile_creator_signature'] = IccProfile.read_int(bytes, 80)
        #self.header['profile_id'] = IccParser.read
        #self.header['reserved'] =


    @staticmethod
    def read_int(bytes, offset, count=4, byteorder='big'):
        return int.from_bytes(bytes[offset:offset+count], byteorder=byteorder)

    @staticmethod
    def read_string(bytes, start, end, byteorder='big'):
        return ''.join(map(chr, bytes[start:end]))

    @staticmethod
    def read_binary_coded_decimal(bytes, start):
        out = "{0}.{1}.{2}".format(bytes[start],
                                   bytes[start+1]>>4,
                                   bytes[start+1]&0x0F)
        return out

    @staticmethod
    def read_datetime(bytes, offset, byteorder='little'):
        return ''