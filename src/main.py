from descriptors.colorhist import ColorHistogram
from readers.ImageReader import ImageReader

__author__ = 'Rigi'

import os
import cv2
import wx
from numpy import *
from hbase import HBase


class MainWindow(wx.Frame):
    # "Constants"
    CF_FEATURE = "feature"
    CF_SEPARATOR = ":"
    TABLE_NAME = "cbir"

    # Members
    db = HBase("localhost")
    dirname = None

    # Constructor
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(460, 200))

        # Create table if necessary
        #self.db.deleteTable(self.tname)
        if MainWindow.TABLE_NAME not in self.db.listTable():
            self.db.createTable(MainWindow.TABLE_NAME, {MainWindow.CF_FEATURE: dict()})

        # A Statusbar in the bottom of the window
        self.sb = self.CreateStatusBar(2)
        self.sb.SetStatusText("Connected to " + self.db.url + " via Thrift.", 1)
        self.gauge = wx.Gauge(self.sb, pos=(5, 2), size=(200, 20))

        # File menu
        filemenu = wx.Menu()
        self.Bind(wx.EVT_MENU, self.OnOpen,
                  filemenu.Append(wx.ID_OPEN, "&Open", ""))
        self.Bind(wx.EVT_MENU, self.OnAbout,
                  filemenu.Append(wx.ID_ABOUT, "&About", " Information about this program"))
        filemenu.AppendSeparator()
        self.Bind(wx.EVT_MENU, self.OnExit,
                  filemenu.Append(wx.ID_EXIT, "E&xit", " Terminate the program"))

        # Command menu
        cmdmenu = wx.Menu()
        self.Bind(wx.EVT_MENU, self.OnRecalcHist,
                  cmdmenu.Append(wx.ID_RESET, "&Histogram", " Recalc Color Histogram Features"))

        # Query menu
        qrymenu = wx.Menu()
        self.Bind(wx.EVT_MENU, self.OnQueryColorHist,
                  qrymenu.Append(wx.ID_RETRY, "&Histogram", " Retrieve images via Color Histogram Features"))

        # Creating the menu bar.
        menubar = wx.MenuBar()
        menubar.Append(filemenu, "&File")
        menubar.Append(cmdmenu, "&Extract Features")
        menubar.Append(qrymenu, "&Query By")
        self.SetMenuBar(menubar)

        # Set the window position and visibility
        self.Centre()
        self.Show(True)

    def OnAbout(self, e):
        # A message dialog box with an OK button. wx.OK is a standard ID in wxWidgets.
        dlg = wx.MessageDialog(self, "A small text editor", "About Sample Editor", wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

    def OnExit(self, e):
        self.Close(True)  # Close the frame.

    def OnOpen(self, e):
        dlg = wx.DirDialog(self, "Choose an image directory")
        if dlg.ShowModal() == wx.ID_OK:
            self.dirname = dlg.GetPath()
            dlg.Destroy()
            self.SetTitle("CBIR (" + self.dirname + ")")

    def OnRecalcHist(self, e):
        if self.dirname:
            images = [os.path.join(self.dirname, f) for f in os.listdir(self.dirname)]
            self.gauge.SetRange(len(images))
            self.gauge.SetValue(0)
            self.sb.SetStatusText("Calculating image histograms.", 1)

            ch = ColorHistogram(ImageReader(images))
            features = ch.extract()

            # TODO: iterate through the features and write into database. Need a Writer object who does the dirty work.
            raise NotImplemented
            # for key, feature in features:
            #     self.db.putValue(MainWindow.TABLE_NAME, key, MainWindow.CF_COLOR_HIST_PREFIX + str(i), h.astype("uint8"))

            #self.gauge.SetValue(self.gauge.GetValue() + 1)

            self.sb.SetStatusText("Image histograms calculated.", 1)
            print "Done."

    def OnQueryColorHist(self, e):
        dlg = wx.FileDialog(self, "Choose a query image")
        if dlg.ShowModal() == wx.ID_OK:
            fname = dlg.GetPath()
            dlg.Destroy()
            img = cv2.imread(fname)
            h0 = cv2.calcHist([img], [0], None, [64], [0, 256])
            h1 = cv2.calcHist([img], [1], None, [64], [0, 256])
            h2 = cv2.calcHist([img], [2], None, [64], [0, 256])
            cv2.normalize(h0, h0, 0, 255, cv2.NORM_MINMAX)
            cv2.normalize(h1, h1, 0, 255, cv2.NORM_MINMAX)
            cv2.normalize(h2, h2, 0, 255, cv2.NORM_MINMAX)
            b = asbytes(h0)
            h0 = fromstring(h0.astype("uint8"), "uint8").astype("float32")
            h1 = fromstring(h1.astype("uint8"), "uint8").astype("float32")
            h2 = fromstring(h2.astype("uint8"), "uint8").astype("float32")
            scan = self.db.scanTable(MainWindow.TABLE_NAME, [MainWindow.CF_COLOR_HIST_0, MainWindow.CF_COLOR_HIST_1, MainWindow.CF_COLOR_HIST_2])
            dist = dict()
            for k, v in scan:
                # img = cv2.imread(k)
                # g0 = cv2.calcHist([img], [0], None, [64], [0, 256])
                # g1 = cv2.calcHist([img], [1], None, [64], [0, 256])
                # g2 = cv2.calcHist([img], [2], None, [64], [0, 256])
                g0 = fromstring(v.get(MainWindow.CF_COLOR_HIST_0), "uint8").astype("float32")
                g1 = fromstring(v.get(MainWindow.CF_COLOR_HIST_1), "uint8").astype("float32")
                g2 = fromstring(v.get(MainWindow.CF_COLOR_HIST_2), "uint8").astype("float32")
                d0 = cv2.compareHist(h0, g0, cv2.cv.CV_COMP_CORREL)
                d1 = cv2.compareHist(h1, g1, cv2.cv.CV_COMP_CORREL)
                d2 = cv2.compareHist(h2, g2, cv2.cv.CV_COMP_CORREL)
                cd0 = cv2.compareHist(h0, g0, cv2.cv.CV_COMP_CHISQR)
                cd1 = cv2.compareHist(h1, g1, cv2.cv.CV_COMP_CHISQR)
                cd2 = cv2.compareHist(h2, g2, cv2.cv.CV_COMP_CHISQR)
                id0 = cv2.compareHist(h0, g0, cv2.cv.CV_COMP_INTERSECT)
                id1 = cv2.compareHist(h1, g1, cv2.cv.CV_COMP_INTERSECT)
                id2 = cv2.compareHist(h2, g2, cv2.cv.CV_COMP_INTERSECT)
                bd0 = cv2.compareHist(h0, g0, cv2.cv.CV_COMP_BHATTACHARYYA)
                bd1 = cv2.compareHist(h1, g1, cv2.cv.CV_COMP_BHATTACHARYYA)
                bd2 = cv2.compareHist(h2, g2, cv2.cv.CV_COMP_BHATTACHARYYA)
                dist[k] = [bd0, bd1, bd2]
                print k, "Correl:", d0, d1, d2, "ChiSQR", cd0, cd1, cd2, "Inter", id0, id1, id2, "Bhatta", bd0, bd1, bd2

#######
# MAIN
#######
app = wx.App(False)
frame = MainWindow(None, "CBIR")
app.MainLoop()