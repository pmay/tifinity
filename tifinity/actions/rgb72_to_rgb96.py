import numpy as np
from numpy.lib.stride_tricks import as_strided


def rgb72_to_rgb96(tiff):
    rawdata = np.frombuffer(tiff.img_data, dtype='B')
    rgbpixels = as_strided(rawdata.view(np.int32), strides=(9, 3,), shape=((1, int(rawdata.shape[0] / 3))))
    rgb = rgbpixels & 0x00ffffff

    # convert: if rgb[0]>0 then (0x80 * rgb[0]) +0x20000000
    def conv(x):
        if x > 0x00:
            x = (0x80 * x) + 0x20000000
        return x

    vconv = np.vectorize(conv)

    rgb32 = vconv(rgb[0])

    tiff.img_data = rgb32.tobytes()

    # now set IFD tag values:
    # bitsPerSample, rowsPerStrip, stripByteCount
    tiff.ifds[0].setBitsPerSample([32, 32, 32])
    tiff.ifds[0].setStripByteCounts([len(tiff.img_data)])
    # tiff.ifds[0].setRowsPerStrip([])
