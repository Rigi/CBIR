from src.comparators.ColorHistCorrel import ColorHistCorrel
from src.db.HBaseWrapper import HBase
from src.descriptors.ColorHistogram import ColorHistogram
from src.readers.ImageReader import ImageReader
from os import path
from os import listdir
import ConfigParser
import wx

__author__ = 'Rigi'


class MainWindow(wx.Frame):
    config = ConfigParser.SafeConfigParser({"host": "localhost", "port": 9090})
    config.read("myconfig.cfg")

    # Members
    db = HBase(config.get("database", "host"),
               config.get("database", "port"))
    dirname = None

    # Constructor
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(460, 200))

        # Create table if necessary
        # self.db.deleteTable(MainWindow.TABLE_NAME)
        if HBase.TABLE_NAME not in self.db.listTable():
            self.db.createTable(HBase.TABLE_NAME, {HBase.CF_FEATURE: dict()})

        # A Statusbar in the bottom of the window
        self.sb = self.CreateStatusBar(2)
        self.sb.SetStatusText("Connected to " + self.db.host + " via Thrift.", 1)
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
                  cmdmenu.Append(wx.ID_ANY, "&Histogram", " Recalc Color Histogram Features"))

        # Query menu
        qrymenu = wx.Menu()
        self.Bind(wx.EVT_MENU, self.OnQueryColorHist,
                  qrymenu.Append(wx.ID_ANY, "&Histogram", " Retrieve images via Color Histogram Features"))

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
        self.db.connection.close()
        self.Close(True)  # Close the frame.

    def OnOpen(self, e):
        dlg = wx.DirDialog(self, "Choose an image directory")
        if dlg.ShowModal() == wx.ID_OK:
            self.dirname = dlg.GetPath()
            dlg.Destroy()
            self.SetTitle("CBIR (" + self.dirname + ")")

    def OnRecalcHist(self, e):
        if self.dirname:
            images = [path.join(self.dirname, f) for f in listdir(self.dirname)]
            self.gauge.SetRange(len(images))
            self.gauge.SetValue(0)
            self.sb.SetStatusText("Calculating image histograms.", 1)

            self.db_hist = ColorHistogram(ImageReader(images))
            self.db_hist.extract()
            self.db.putValues(HBase.TABLE_NAME,
                              ColorHistogram.CQ_COLOR_HIST,
                              self.db_hist.tostring())

            self.sb.SetStatusText("Image histograms recalculated.", 1)
            print "Done."

    def OnQueryColorHist(self, e):
        dlg = wx.FileDialog(self, "Choose a query image")
        if dlg.ShowModal() == wx.ID_OK:
            fname = dlg.GetPath()
            dlg.Destroy()

            self.q_hist = ColorHistogram(ImageReader([fname]))
            self.q_hist.extract()

            self.cmp = ColorHistCorrel()
            #print self.cmp.get_distance(self.q_hist, self.db_hist)

            scan = self.db.scanTable(HBase.TABLE_NAME,
                                     [ColorHistogram.CQ_COLOR_HIST])

            self.db_hist2 = ColorHistogram.init_from_db(scan)
            d = self.cmp.get_distance(self.q_hist, self.db_hist2)
            dlist = sorted(d.items(), key=lambda t: t[1], reverse=True)
            for item in dlist[:5]:
                print item

#######
# MAIN
#######
app = wx.App(False)
frame = MainWindow(None, "CBIR")
app.MainLoop()