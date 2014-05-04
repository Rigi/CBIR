import cv2
from src.comparators.AbstractComparator import AbstractComparator
from src.descriptors.ColorHistogram import ColorHistogram

__author__ = 'Rigi'


class ColorHistCorrel(AbstractComparator):

    def __init__(self):
        super(ColorHistCorrel, self).__init__()

    @classmethod
    def acceptable_classes(cls):
        return [ColorHistogram]

    def get_distance(self, query_hist, ref_hist, w=[1.0, 1.0, 1.0]):
        result = dict()

        r0, v0 = query_hist.features.items()[0]
        for r1, v1 in ref_hist.features.items():
            result[r1] = cv2.compareHist(v0[0], v1[0], cv2.cv.CV_COMP_CORREL) * w[0] + \
                    cv2.compareHist(v0[1], v1[1], cv2.cv.CV_COMP_CORREL) * w[1] + \
                    cv2.compareHist(v0[2], v1[2], cv2.cv.CV_COMP_CORREL) * w[2]

        return result
