import numpy as np
from numpy.lib.stride_tricks import as_strided

class rgb72_to_rgb96():

    def __init__(self):
        self._vconv = np.vectorize(self._convert)

    @staticmethod
    def _convert(x):
        """Helper conversion function: if rgb[0]>0 then (0x80 * rgb[0])+0x20000000 else 0x00"""
        if x > 0x00:
            x = (0x80 * x) + 0x20000000
        return x

    def migrate(self, tiff):
        """Converts a 24 bit per channel pixel to a 32 bit per channel floating point value."""
        # TODO: Check if tiff is a 72bpc image first

        for ifd in tiff.ifds:
            # need to limit striding to complete pixel ranges during conversion.
            completerange = ifd.img_data.shape[0] - ifd.img_data.shape[0]%12
            raw = ifd.img_data[:completerange]
            
            rgbpixels = as_strided(raw.view(np.int32), strides=(9, 3,), shape=(1, int(raw.shape[0] / 3)))
            rgb = rgbpixels & 0x00ffffff

            rgb32 = self._vconv(rgb[0])
            ifd.img_data = rgb32.view(dtype='uint8')

            # now set IFD tag values:
            # bitsPerSample, rowsPerStrip, stripByteCount
            ifd.set_bits_per_sample([32, 32, 32])
            ifd.set_strip_byte_counts([len(ifd.img_data)])
            # tiff.ifds[0].setRowsPerStrip([])
