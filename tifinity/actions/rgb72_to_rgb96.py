import numpy as np
from numpy.lib.stride_tricks import as_strided


def _convert(x):
    """Helper conversion function: if rgb[0]>0 then (0x80 * rgb[0])+0x20000000 else 0x00"""
    if x > 0x00:
        x = (0x80 * x) + 0x20000000
    return x


_vconv = np.vectorize(_convert)


def rgb72_to_rgb96(tiff):
    """Converts a 24 bit per channel pixel to a 32 bit per channel floating point value."""
    # TODO: Check if tiff is a 72bpc image first

    for ifd in tiff.ifds:
        rgbpixels = as_strided(ifd.img_data.view(np.int32), strides=(9, 3,), shape=(1, int(ifd.img_data.shape[0] / 3)))
        rgb = rgbpixels & 0x00ffffff

        rgb32 = _vconv(rgb[0])
        ifd.img_data = rgb32.view(dtype='uint8')

        # now set IFD tag values:
        # bitsPerSample, rowsPerStrip, stripByteCount
        ifd.set_bits_per_sample([32, 32, 32])
        ifd.set_strip_byte_counts([len(ifd.img_data)])
        # tiff.ifds[0].setRowsPerStrip([])
