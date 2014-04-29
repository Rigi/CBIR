from wx import *

__author__ = 'Rigi'


class ImagePresenter(Frame):
    max_result = 6

    def __init__(self, distances, *args, **kwargs):
        super(ImagePresenter, self).__init__(*args, **kwargs)

        self.distances = distances[:ImagePresenter.max_result]
        self.InitUI()
        self.SetTitle("Results")

    def InitUI(self):
        sizer = GridSizer(cols=3, vgap=20, hgap=5)

        for uri, fitness in self.distances:
            bmp = Image(uri).ConvertToBitmap()
            item = BoxSizer(VERTICAL)
            item.Add(StaticText(self, label="Fitness: " + str(fitness)))
            item.Add(StaticBitmap(self, bitmap=bmp, size=(bmp.GetWidth(), bmp.GetHeight())))
            sizer.Add(item)

        self.SetClientSize(sizer.GetMinSize())
        self.SetSizer(sizer)
