import cv2

__author__ = 'Rigi'


class ImageReader():
    def __init__(self, paths):
        self.paths = paths

    def __iter__(self):
        for path in self.paths:
            yield (path, cv2.imread(path))
