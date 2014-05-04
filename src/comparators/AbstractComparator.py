import abc
__author__ = 'Rigi'


class AbstractComparator():
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        pass

    @abc.abstractproperty
    @classmethod
    def acceptable_classes(cls):
        pass

    @classmethod
    def is_acceptable(cls, clazz):
        return clazz in cls.acceptable_classes()