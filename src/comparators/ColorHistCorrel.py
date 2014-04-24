import cv2

__author__ = 'Rigi'


class ColorHistCorrel():
    def __init__(self):
        pass

    def get_distance(self, query_hist, db_hist, w=[1.0, 1.0, 1.0]):
        result = dict()

        r0, v0 = query_hist.features.items()[0]
        for r1, v1 in db_hist.features.items():
            result[r1] = cv2.compareHist(v0[0], v1[0], cv2.cv.CV_COMP_CORREL) * w[0] + \
                    cv2.compareHist(v0[1], v1[1], cv2.cv.CV_COMP_CORREL) * w[1] + \
                    cv2.compareHist(v0[2], v1[2], cv2.cv.CV_COMP_CORREL) * w[2]

        return result