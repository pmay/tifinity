import json
import math
import os

from tifinity.actions.checksum import Checksum
from tifinity.modules import BaseModule
from tifinity.parser.tiff import Tiff
from tifinity.scripts.timing import time_usage

from colormath.color_objects import AdobeRGBColor, sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000
from colormath.color_diff import delta_e_cie1976

import colormath.color_diff_matrix as cdm

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
        m_parser.add_argument("--colormath", dest="colormath", action="store_true", help="Use Colormath approach if true")
        m_parser.add_argument("-o", dest="output", help="An output filename to use (for png, txt file, etc)")

        m_parser.add_argument("tiff1", help="the original TIFF file to compare")
        m_parser.add_argument("tiff1_prof", help="the color profile of the first tiff", choices=['AdobeRGB', 'sRGB', 'LAB'],
                              default='sRGB')
        m_parser.add_argument("tiff2", help="the comparison TIFF file")
        m_parser.add_argument("tiff2_prof", help="the color profile of the 2nd tiff", choices=['AdobeRGB', 'sRGB', 'LAB'],
                              default='sRGB')

    #@time_usage
    def process_cli(self, args):
        try:
            # Load TIFFs
            tiff1 = Tiff(args.tiff1)
            tiff2 = Tiff(args.tiff2)
        except AttributeError:
            raise

        assert(tiff1.ifds[0].get_bits_per_sample() == [8,8,8])

        self.returnValues = {}
        if args.colormath:
            distances = self.calculate_distances_2(tiff1, tiff2, args)
        else:
            distances = self.calculate_distance(tiff1, tiff2, args)

        if args.graph:
            self.graph_distances(tiff1.ifds[0].get_image_width(), distances, args)
        else:
            count = 0
            for d in distances:
                print(d)

                count += 1
                if count == 10:
                    break

    def calculate_distance(self, tiff1, tiff2, args, limit=None):
        print("\nLoading Tiff 1...")
        img1data = tiff1.ifds[0].img_data
        img1_norm = img1data / 255             # normalise (same if RGB or AdobeRGB
        img1_col = np.reshape(img1_norm, (int(img1_norm.shape[0] / 3), 3))  # split into separate RGB arrays

        print("Loading Tiff 2...")
        img2data = tiff2.ifds[0].img_data
        img2_norm = img2data / 255  # normalise (same if RGB or AdobeRGB
        img2_col = np.reshape(img2_norm, (int(img2_norm.shape[0] / 3), 3))  # split into separate RGB arrays

        # convert to LAB
        print("Converting Tiff 1 to LAB")
        img1_xyz = PerceptualValidation.np_rgb_to_xyz(img1_col[0:limit], args.tiff1_prof)
        img1_lab = PerceptualValidation.np_xyz_to_lab(img1_xyz, args.tiff1_prof)

        print("Converting Tiff 2 to LAB")
        img2_xyz = PerceptualValidation.np_rgb_to_xyz(img2_col[0:limit], args.tiff2_prof)
        img2_lab = PerceptualValidation.np_xyz_to_lab(img2_xyz, args.tiff2_prof)

        print("Calculating Delta-e")
        distances = PerceptualValidation.cielab_diff_p(img1_lab, img2_lab)
        np.savetxt(args.output + "_dist.txt", distances)

        return distances



    def calculate_distances_2(self, tiff1, tiff2, args, limit=None):
        print("\nLoading Tiff 1...")
        img1data = tiff1.ifds[0].img_data
        img1_col = PerceptualValidation.arrayToColor(img1data, args.tiff1_prof, limit)

        # if args.tiff1_prof != 'LAB':
        #     img1_col = PerceptualValidation.arrayToColor(tiffs[0].ifds[0].img_data, args.tiff1_prof)
        # else:
        #     #img1_col = PerceptualValidation.arrayToVector(tiffs[0].ifds[0].img_data)
        #     imgdata = tiffs[0].ifds[0].img_data
        #     img1_col = np.reshape(imgdata, (int(imgdata.shape[0] / 3), 3))

        print("Loading Tiff 2...")
        img2data = tiff2.ifds[0].img_data
        img2_col = PerceptualValidation.arrayToColor(img2data, args.tiff2_prof, limit)

        # if args.tiff2_prof != 'LAB':
        #     img2_col = PerceptualValidation.arrayToColor(tiffs[1].ifds[0].img_data, args.tiff2_prof)
        # else:
        #     #img2_col = PerceptualValidation.arrayToMatrix(tiffs[1].ifds[0].img_data)
        #     imgdata = tiffs[1].ifds[0].img_data
        #     img2_col = np.reshape(imgdata, (int(imgdata.shape[0] / 3), 3))

        print("Converting Tiff 1 to LAB")
        img1_lab = PerceptualValidation.arrayToLABColor(img1_col)

        # if args.tiff1_prof != 'LAB':
        #     print("Converting Tiff 1 to LAB")
        #     img1_lab = PerceptualValidation.arrayToLABColor(img1_col)
        # else:
        #     img1_lab = img1_col

        print("Converting Tiff 2 to LAB")
        img2_lab = PerceptualValidation.arrayToLABColor(img2_col)

        # if args.tiff2_prof != 'LAB':
        #     print("Converting Tiff 2 to LAB")
        #     img2_lab = PerceptualValidation.arrayToLABColor(img2_col)
        # else:
        #     img2_lab = img2_col

        # print(PerceptualValidation.euclid(img1_lab[0], img2_lab[0]))

        print("Calculating Delta-e")
        distances = PerceptualValidation.cielab_diff(img1_lab, img2_lab)
        np.savetxt(args.output + "_colormath_dist.txt", distances)

        return distances

    def graph_distances(self, x_dim, distances, args):
        # graph distances
        plt.figure()
        plt.subplot(1, 2, 1)
        plt.hist(distances, density=False, bins=30)
        plt.xlabel('CIE1976 Delta-E')
        plt.ylabel('Count')

        # heatmap
        plt.subplot(1, 2, 2)

        hmap_distances = np.reshape(distances, (-1, x_dim))
        plt.imshow(hmap_distances)
        # plt.show()

        fname = args.output
        if args.colormath:
            fname = fname + "_colormath"
        plt.savefig(fname + ".png")


### Calculate_distances_1 functions below ###
    @staticmethod
    def inv_companding_rgb(val):
        if val <= 0.04045:
            return val / 12.92
        else:
            return math.pow((val + 0.055) / 1.055, 2.4)

    @staticmethod
    def inv_companding_adobe(val):
        return math.pow(val, 2.2)

    @staticmethod
    def apply_rgb_matrix(val, matrix):
        return np.dot(matrix, val)

    @staticmethod
    def validate(val):
        if val < 0:
            return 0
        return val

    conv_matrix = {
        'sRGB': np.array((
            (0.412424, 0.357579, 0.180464),
            (0.212656, 0.715158, 0.0721856),
            (0.0193324, 0.119193, 0.950444))),
        'AdobeRGB': np.array((
            (0.576700, 0.185556, 0.188212),
            (0.297361, 0.627355, 0.0752847),
            (0.0270328, 0.0706879, 0.991248))),
    }

    @staticmethod
    @time_usage
    def np_rgb_to_xyz(rgb, fromProfile):
        if fromProfile == 'sRGB':
            lin_rgb = np.vectorize(PerceptualValidation.inv_companding_rgb)(rgb)

        if fromProfile == 'AdobeRGB':
            lin_rgb = np.vectorize(PerceptualValidation.inv_companding_adobe)(rgb)

        result_matrix = np.apply_along_axis(PerceptualValidation.apply_rgb_matrix, 1, lin_rgb, PerceptualValidation.conv_matrix[fromProfile])
        return np.vectorize(PerceptualValidation.validate)(result_matrix)


    @staticmethod
    def calc_temp(val, ref):
        return val / ref

    @staticmethod
    def calc_intermediates(val):
        if val > 0.008856:
            return math.pow(val, (1.0 / 3.0))
        else:
            return (7.787 * val) + (16.0 / 116.0)

    @staticmethod
    def calc_lab(val):
        lab_l = (116.0 * val[1]) - 16.0
        lab_a = 500.0 * (val[0] - val[1])
        lab_b = 200.0 * (val[1] - val[2])
        return np.array([lab_l, lab_a, lab_b])

    # From http://www.brucelindbloom.com/index.html?Eqn_ChromAdapt.html
    illuminants = {
        'd50': (0.96422, 1.00000, 0.82521),
        'd65': (0.95047, 1.00000, 1.08883),
    }

    @staticmethod
    @time_usage
    def np_xyz_to_lab(xyz, fromProfile, illuminant='d65'):
        #ref_white = PerceptualValidation.apply_rgb_matrix(np.array([1.0,1.0,1.0]), PerceptualValidation.conv_matrix[fromProfile])
        # Take a pre-calculated white reference point, rather than calculate directly - difference is precision.
        ref_white = np.array(PerceptualValidation.illuminants[illuminant])
        temp_lab = np.apply_along_axis(PerceptualValidation.calc_temp, 1, xyz, ref_white)
        inter_lab = np.vectorize(PerceptualValidation.calc_intermediates)(temp_lab)

        return np.apply_along_axis(PerceptualValidation.calc_lab, 1, inter_lab)


    # @staticmethod
    # @time_usage
    # def np_arrayToColor(imgdata, fromProfile):
    #     # assume 8 bit
    #     # img = as_strided(imgdata, strides=(3, 1), shape=(int(imgdata.shape[0] / 3), 3))
    #     c1 = imgdata[0::3][:100]
    #     c2 = imgdata[1::3][:100]
    #     c3 = imgdata[2::3][:100]
    #
    #     # if tiff.ifds[0].get_tag_value_by_name('PhotometricInterpretation') == 2:
    #     if fromProfile == 'AdobeRGB':
    #         colors = np.vectorize(PerceptualValidation.adobe_to_LAB)(c1, c2, c3)
    #     #            colors = map(lambda c: AdobeRGBColor(c[0], c[1], c[2], is_upscaled=True), img)
    #     if fromProfile == 'sRGB':
    #         # normalise
    #         colors = np.vectorize(PerceptualValidation.srgb_to_LAB)(c1, c2, c3)
    #     if fromProfile == 'LAB':
    #         colors = np.vectorize(PerceptualValidation.lab_to_LAB)(c1, c2, c3)
    #
    #     return colors



    @staticmethod
    def getAsVector(c1, c2, c3):
        return np.array([c1, c2, c3], dtype=float)

    @staticmethod
    def getAsMatrix(c1, c2, c3):
        return np.array([(c1, c2, c3)], dtype=float)

    @staticmethod
    @time_usage
    def arrayToVector(imgdata):
        c1 = imgdata[0::3]
        c2 = imgdata[1::3]
        c3 = imgdata[2::3]
        return np.vectorize(PerceptualValidation.getAsVector)(c1, c2, c3)

    @staticmethod
    @time_usage
    def arrayToMatrix(imgdata):
        c1 = imgdata[0::3]
        c2 = imgdata[1::3]
        c3 = imgdata[2::3]
        return np.vectorize(PerceptualValidation.getAsMatrix)(c1, c2, c3)

    @staticmethod
    def euclid(a, b):
        return np.linalg.norm(a-b)

    @staticmethod
    @time_usage
    def cielab_diff_p(lab1, lab2):
        result = np.empty(lab1.shape[0])
        for i,(a,b) in enumerate(zip(lab1, lab2)):
            result[i] = PerceptualValidation.euclid(a, b)

        # for i in range(10):
        #     print("{0}\t{1}\t{2}".format(lab1[i], lab2[i], result[i]))
        return result
        #return np.vectorize(cdm.delta_e_cie1976)(lab1, lab2)

        #return np.vectorize(PerceptualValidation.euclid)(lab1, lab2)
        #return np.apply_along_axis(PerceptualValidation.euclid, 1, zipped)


### ColorMath direct approach below ###

    @staticmethod
    def adobe_to_LAB(c1, c2, c3):
        return AdobeRGBColor(c1, c2, c3, is_upscaled=True)

    @staticmethod
    def srgb_to_LAB(c1, c2, c3):
        return sRGBColor(c1, c2, c3, is_upscaled=True)

    @staticmethod
    def lab_to_LAB(c1, c2, c3):
        return LabColor(c1, c2, c3)

    @staticmethod
    @time_usage
    def arrayToColor(imgdata, fromProfile, limit=None):
        # assume 8 bit
        # img = as_strided(imgdata, strides=(3, 1), shape=(int(imgdata.shape[0] / 3), 3))
        c1 = imgdata[0::3][0:limit]
        c2 = imgdata[1::3][0:limit]
        c3 = imgdata[2::3][0:limit]

        # if tiff.ifds[0].get_tag_value_by_name('PhotometricInterpretation') == 2:
        if fromProfile == 'AdobeRGB':
            colors = np.vectorize(PerceptualValidation.adobe_to_LAB)(c1, c2, c3)
        #            colors = map(lambda c: AdobeRGBColor(c[0], c[1], c[2], is_upscaled=True), img)
        if fromProfile == 'sRGB':
            #            colors = map(lambda c: sRGBColor(c[0], c[1], c[2], is_upscaled=True), img)
            colors = np.vectorize(PerceptualValidation.srgb_to_LAB)(c1, c2, c3)
        if fromProfile == 'LAB':
            colors = np.vectorize(PerceptualValidation.lab_to_LAB)(c1, c2, c3)

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

        # for i in range(10):
        #     print("{0}\t{1}\t{2}".format(lab1[i], lab2[i], distances[i]))
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
