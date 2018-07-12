import json

from tifinity.actions.checksum import Checksum
from tifinity.modules import BaseModule
from tifinity.parser.tiff import Tiff
from tifinity.scripts.timing import time_usage

from colormath.color_objects import AdobeRGBColor, sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000
from colormath.color_diff import delta_e_cie1976

import numpy as np
from numpy.lib.stride_tricks import as_strided

from tifinity.scripts.timing import time_usage

import matplotlib.pyplot as plt

class PerceptualValidation(BaseModule):
    """ Module comparing the visual similarity of two TIFF files."""

    def __init__(self):
        self.cli_name = 'perceptual'
        #self.metric_choices = ['checksum', 'checksum-images']      # other metric choices may be added
        # defaults
        self.json = False

    def add_subparser(self, mainparser):
        m_parser = mainparser.add_parser(self.cli_name)
        m_parser.set_defaults(func=self.process_cli)

        #m_parser.add_argument("-m", "--metric", dest="metric", choices=self.metric_choices, required=True)

        m_parser.add_argument("--json", dest="json", action="store_true", help="output in json format")
        m_parser.add_argument("--graph", dest="graph", action="store_true", help="plot graphs of differences")

        m_parser.add_argument("tiff1", help="the original TIFF file to compare")
        m_parser.add_argument("tiff1_prof", help="the color profile of the first tiff", choices=['AdobeRGB', 'sRGB'],
                              default='sRGB')
        m_parser.add_argument("tiff2", help="the comparison TIFF file")
        m_parser.add_argument("tiff2_prof", help="the color profile of the 2nd tiff", choices=['AdobeRGB', 'sRGB'],
                              default='sRGB')

    #@time_usage
    def process_cli(self, args):
        try:
            # Load TIFFs
            tiffs = [Tiff(args.tiff1), Tiff(args.tiff2)]
        except AttributeError:
            raise

        assert(tiffs[0].ifds[0].get_bits_per_sample() == [8,8,8])

        self.returnValues = {}

        img1 = tiffs[0].ifds[0].img_data
        img2 = tiffs[1].ifds[0].img_data

        img1_col = PerceptualValidation.arrayToColor(img1, args.tiff1_prof)
        img2_col = PerceptualValidation.arrayToColor(img2, args.tiff2_prof)

        img1_lab = PerceptualValidation.arrayToLABColor(img1_col)
        img2_lab = PerceptualValidation.arrayToLABColor(img2_col)

        # check PhotometricInterpretation and change to Lab Color Space as necessary
        # if tiff[0].ifds[0].get_tag_value_by_name('PhotometricInterpretation') != 8:
        #     img1 =

        distances = PerceptualValidation.cielab_diff(img1_lab, img2_lab)

        # graph distances
        if args.graph:
            #d = list(distances)
            plt.hist(distances, normed=True, bins=30)
            plt.ylabel('Count');

        else:
            count = 0
            #for (c1, c2, d) in distances:
            #    print("{0}\t{1}\t{2}".format(c1, c2, d))
            for d in distances:
                print (d)

                count += 1
                if count==10:
                    break


        # image_identical = {}
        # i = 0
        # for i_orig in checksums[0]["images"]:
        #     image_identical[i] = []                             # for each image in the original TIFF
        #     for i_other in checksums[1]["images"]:
        #         image_identical[i].append(i_orig == i_other)    # compare against each image in the comparison TIFF
        #     i += 1
        # self.returnValues["Images Identical"] = image_identical

        #output = self.format_output(args.json)
        # print(output)
        # return output

    @staticmethod
    def adobe_to_LAB(c1, c2, c3):
        return AdobeRGBColor(c1, c2, c3, is_upscaled=True)

    @staticmethod
    def srgb_to_LAB(c1, c2, c3):
        return sRGBColor(c1, c2, c3, is_upscaled=True)

    @staticmethod
    @time_usage
    def arrayToColor(imgdata, fromProfile):
        # assume 8 bit
        # img = as_strided(imgdata, strides=(3, 1), shape=(int(imgdata.shape[0] / 3), 3))
        c1 = imgdata[0::3][:1000000]
        c2 = imgdata[1::3][:1000000]
        c3 = imgdata[2::3][:1000000]

        # if tiff.ifds[0].get_tag_value_by_name('PhotometricInterpretation') == 2:
        if fromProfile == 'AdobeRGB':
            colors = np.vectorize(PerceptualValidation.adobe_to_LAB)(c1, c2, c3)
        #            colors = map(lambda c: AdobeRGBColor(c[0], c[1], c[2], is_upscaled=True), img)
        if fromProfile == 'sRGB':
            #            colors = map(lambda c: sRGBColor(c[0], c[1], c[2], is_upscaled=True), img)
            colors = np.vectorize(PerceptualValidation.srgb_to_LAB)(c1, c2, c3)

        return colors

    @staticmethod
    @time_usage
    def arrayToLABColor(colors):
        #return map(lambda c: convert_color(c, LabColor), colors)
        return np.vectorize(convert_color)(colors, LabColor)

    @staticmethod
    @time_usage
    def cielab_diff(lab1, lab2):
#        labcols = zip(lab1, lab2)

        # pixel wise euclidean distance
        #distances = map(lambda a: (a[0], a[1], delta_e_cie1976(a[0], a[1])), labcols)
#        distances = map(lambda a: delta_e_cie1976(a[0], a[1]), labcols)
        distances = np.vectorize(delta_e_cie1976)(lab1, lab2)
        return distances


    # @staticmethod
    # def toLabColor(c_list):
    #     return LabColor(c_list[0], c_list[1], c_list[2])

    # @staticmethod
    # def cielab_diff(img1, img2):
    #     assert (len(img1) == len(img2))
    #
    #     im1 = as_strided(img1, strides=(3, 1), shape=(int(img1.shape[0] / 3), 3))
    #     im2 = as_strided(img2, strides=(3, 1), shape=(int(img2.shape[0] / 3), 3))
    #
    #     labcols = zip(map(toLabColor, im1), map(toLabColor, im2))
    #
    #     # pixel wise euclidean distance
    #     distances = map(lambda a: delta_e_cie1976(a[0], a[1]), labcols)
    #     return distances


    def format_output(self, jsonout=False):
        if jsonout:
            return json.dumps(self.returnValues)
        else:
            out = ""
            if "Files Identical" in self.returnValues:
                out += "Files Identical:\t{ident}\n".format(ident=self.returnValues["Files Identical"])
            for x in sorted(self.returnValues["Images Identical"].keys()):
                count=0
                for y in self.returnValues["Images Identical"][x]:
                    out += "Tiff[1].Image[{id}] - Tiff[2].Image[{idy}]:\t{ident}\n".format(id=x, idy=count, ident=y)
                    count+=1

            return out

module = PerceptualValidation()     # initiate module class when module imported
