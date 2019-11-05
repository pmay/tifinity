import json
import math
import os

from tifinity.modules import BaseModule
from tifinity.parser.tiff import Tiff
from tifinity.scripts.timing import time_usage

import numpy as np

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
        print("\nConverting Tiff 1 to CIELAB...")
        img1_lab = PerceptualValidation.convert_tiff_to_lab(tiff1, args.tiff1_prof, args.limit)

        print("Converting Tiff 2 to CIELAB...")
        img2_lab = PerceptualValidation.convert_tiff_to_lab(tiff2, args.tiff2_prof, args.limit)

        print("Calculating perceptual pixel differences...")
        distances = PerceptualValidation.calculate_distance(img1_lab, img2_lab, args.output)

        if args.graph:
            PerceptualValidation.graph_distances(tiff1.ifds[0].get_image_width(), distances, args)
        else:
            count = 0
            for d in distances:
                print(d)

                count += 1
                if count == 10:
                    break

    @staticmethod
    def calculate_distance(img1_lab, img2_lab, output=None):
        print("Calculating Delta-e")
        distances = PerceptualValidation.cielab_diff_p(img1_lab, img2_lab)

        if output:
            print("Saving Delta-e")
            np.savetxt(output + "_dist.txt", distances)

        return distances

    @staticmethod
    def convert_tiff_to_lab(tiff, profile, limit=None):
        """Converts a TIFF file to lab format"""
        print("\nLoading Tiff...")
        img_data = tiff.ifds[0].img_data
        img_norm = img_data / 255  # normalise (same if RGB or AdobeRGB)
        img_col = np.reshape(img_norm, (int(img_norm.shape[0] / 3), 3))  # split into separate RGB arrays

        # convert to LAB
        print("Converting Tiff to LAB...")
        img_xyz = PerceptualValidation.np_rgb_to_xyz(img_col[0:limit], profile)
        img_lab = PerceptualValidation.np_xyz_to_lab(img_xyz, profile)

        return img_lab

    @staticmethod
    def graph_distances(x_dim, distances, output):
        # number pixels >2.0
        gt = (distances > 2.0).sum()

        # graph distances
        plt.figure()
        plt.subplot(1, 2, 1)
        plt.hist(distances, density=False, bins=30)
        plt.xlabel('CIE1976 Delta-E')
        plt.ylabel('Count')
        plt.title("#pixels >2: " + str(gt), fontsize=10)
        plt.axvline(x=2, color='red')



        # heatmap
        plt.subplot(1, 2, 2)
        hmap_distances = np.reshape(distances, (-1, x_dim))
        plt.imshow(hmap_distances)
        # plt.show()

        # TODO: output filename processing too specific to a particular filename encoding
        splt_out = output.rsplit('_[', 1)
        file = splt_out[0].rsplit('/', 1)[1]+".tif"
        cmd = splt_out[1][:-1].rsplit('_vs_')
        t1cmd = cmd[0].rsplit('-')
        t2cmd = cmd[1].rsplit('-')

        title = "Perceptual difference for: "+file+"\nTiff 1: "+t1cmd[0]+" data; "+t1cmd[1]+" profile\nTiff 2: "+t2cmd[0]+" data; "+t2cmd[1]+" profile\n"
        plt.suptitle(title)
        plt.subplots_adjust(top=0.8, wspace=0.4)



        plt.savefig(output + ".png")


### Calculate_distances functions below ###
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

### To calc timings for each part

    @staticmethod
    @time_usage
    def get_temp_lab(xyz, ref_white):
        return np.apply_along_axis(PerceptualValidation.calc_temp, 1, xyz, ref_white)

    @staticmethod
    @time_usage
    def get_calc_intermediates(temp_lab):
        return np.vectorize(PerceptualValidation.calc_intermediates)(temp_lab)

    @staticmethod
    @time_usage
    def calculate_lab(inter_lab):
        return np.apply_along_axis(PerceptualValidation.calc_lab, 1, inter_lab)

### End split timings

    @staticmethod
    @time_usage
    def np_xyz_to_lab(xyz, fromProfile, illuminant='d65'):
        #ref_white = PerceptualValidation.apply_rgb_matrix(np.array([1.0,1.0,1.0]), PerceptualValidation.conv_matrix[fromProfile])
        # Take a pre-calculated white reference point, rather than calculate directly - difference is precision.
        ref_white = np.array(PerceptualValidation.illuminants[illuminant])
        #temp_lab = np.apply_along_axis(PerceptualValidation.calc_temp, 1, xyz, ref_white)
        temp_lab = PerceptualValidation.get_temp_lab(xyz, ref_white)
        #inter_lab = np.vectorize(PerceptualValidation.calc_intermediates)(temp_lab)
        inter_lab = PerceptualValidation.get_calc_intermediates(temp_lab)

        #return np.apply_along_axis(PerceptualValidation.calc_lab, 1, inter_lab)
        return PerceptualValidation.calculate_lab(inter_lab)


    # @staticmethod
    # def getAsVector(c1, c2, c3):
    #     return np.array([c1, c2, c3], dtype=float)
    #
    # @staticmethod
    # def getAsMatrix(c1, c2, c3):
    #     return np.array([(c1, c2, c3)], dtype=float)
    #
    # @staticmethod
    # @time_usage
    # def arrayToVector(imgdata):
    #     c1 = imgdata[0::3]
    #     c2 = imgdata[1::3]
    #     c3 = imgdata[2::3]
    #     return np.vectorize(PerceptualValidation.getAsVector)(c1, c2, c3)
    #
    # @staticmethod
    # @time_usage
    # def arrayToMatrix(imgdata):
    #     c1 = imgdata[0::3]
    #     c2 = imgdata[1::3]
    #     c3 = imgdata[2::3]
    #     return np.vectorize(PerceptualValidation.getAsMatrix)(c1, c2, c3)

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
