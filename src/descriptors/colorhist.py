import cv2
from abstractdesc import AbstractDescriptor

__author__ = 'Rigi'


class ColorHistogram(AbstractDescriptor):
    CF_COLOR_HIST_0 = "color_hist_0"
    CF_COLOR_HIST_1 = "color_hist_1"
    CF_COLOR_HIST_2 = "color_hist_2"

    def __init__(self, i_source):
        super(ColorHistogram, self).__init__(i_source)

    def extract(self):
        result = dict()
        for path, img in self.source:
            h = dict()
            i = 0
            for cf in [ColorHistogram.CF_COLOR_HIST_0, ColorHistogram.CF_COLOR_HIST_1, ColorHistogram.CF_COLOR_HIST_2]:
                tmp = cv2.calcHist([img], [i], None, [64], [0, 256])
                cv2.normalize(tmp, tmp, 0, 255, cv2.NORM_MINMAX)
                h[cf] = tmp
                i += 1
            result[path] = h
        return result

    def tostring(self):
        super(ColorHistogram, self).tostring()

    def fromstring(self, i_str):
        super(ColorHistogram, self).fromstring(i_str)
