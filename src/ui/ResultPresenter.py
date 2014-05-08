from wx import Panel
import wx

__author__ = 'Rigi'


class ImagePresenter(Panel):
    MAX_RESULT = 6

    def __init__(self, distances, *args, **kwargs):
        super(ImagePresenter, self).__init__(*args, **kwargs)

        self.distances = distances[:ImagePresenter.MAX_RESULT]
        self.InitUI()

    def InitUI(self):
        sizer = wx.GridSizer(cols=3, vgap=20, hgap=5)

        for uri, fitness in self.distances:
            bmp = wx.Image(uri).ConvertToBitmap()
            item = wx.BoxSizer(wx.VERTICAL)
            item.Add(wx.StaticText(self, label="Fitness: " + str(fitness)))
            item.Add(wx.StaticBitmap(self, bitmap=bmp, size=(bmp.GetWidth(), bmp.GetHeight())))
            sizer.Add(item)

        self.SetClientSize(sizer.GetMinSize())
        self.SetSizer(sizer)
