from src.comparators.ColorHistCorrel import ColorHistCorrel
from src.db.HBaseWrapper import HBase
from src.descriptors.ColorHistogram import ColorHistogram
from src.query.SimpleQuery import SimpleQuery
from src.readers.ImageReader import ImageReader
from os import path
from os import listdir
import ConfigParser
import wx

__author__ = 'Rigi'


class MainWindow(wx.Frame):
    config = ConfigParser.SafeConfigParser({"host": "localhost", "port": 9090})
    config.read("../myconfig.cfg")

    # Members
    db = HBase(config.get("database", "host"),
               config.get("database", "port"))
    dir_name = None

    # Constructor
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(460, 200))

        # Create table if necessary
        # self.db.deleteTable()
        # self.db.removeInvalidImages()
        self.db.createTable(HBase.TABLE_NAME, {HBase.CF_FEATURE: dict()})

        # A status bar in the bottom of the window
        self.sb = self.CreateStatusBar(2)
        self.sb.SetStatusText("Connected to " + self.db.host + " via Thrift.", 1)
        self.gauge = wx.Gauge(self.sb, pos=(5, 2), size=(200, 20))

        # File menu
        file_menu = wx.Menu()
        self.Bind(wx.EVT_MENU, self.OnOpen,
                  file_menu.Append(wx.ID_OPEN, "&Open", ""))
        self.Bind(wx.EVT_MENU, self.OnAbout,
                  file_menu.Append(wx.ID_ABOUT, "&About", " Information about this program"))
        file_menu.AppendSeparator()
        self.Bind(wx.EVT_MENU, self.OnExit,
                  file_menu.Append(wx.ID_EXIT, "E&xit", " Terminate the program"))

        # Command menu
        cmd_menu = wx.Menu()
        self.Bind(wx.EVT_MENU, self.OnRecalcHist,
                  cmd_menu.Append(wx.ID_ANY, "&Histogram", " Recalc Color Histogram Features"))

        # Query menu
        qry_menu = wx.Menu()
        self.Bind(wx.EVT_MENU, self.OnQueryColorHist,
                  qry_menu.Append(wx.ID_ANY, "&Histogram", " Retrieve images via Color Histogram Features"))

        # Creating the menu bar.
        menu_bar = wx.MenuBar()
        menu_bar.Append(file_menu, "&File")
        menu_bar.Append(cmd_menu, "&Extract Features")
        menu_bar.Append(qry_menu, "&Query By")
        self.SetMenuBar(menu_bar)

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
            self.dir_name = dlg.GetPath()
            dlg.Destroy()
            self.SetTitle("CBIR (" + self.dir_name + ")")

    def OnRecalcHist(self, e):
        if self.dir_name:
            images = [path.join(self.dir_name, f) for f in listdir(self.dir_name)]
            self.gauge.SetRange(len(images))
            self.gauge.SetValue(0)
            self.sb.SetStatusText("Calculating image histograms.", 1)

            db_hist = ColorHistogram(ImageReader(images))
            db_hist.extract()
            self.db.putValues(HBase.TABLE_NAME,
                              ColorHistogram.CQ_COLOR_HIST,
                              db_hist.tostring())

            self.sb.SetStatusText("Image histograms recalculated.", 1)
            print "Done."

    def OnQueryColorHist(self, e):
        dlg = wx.FileDialog(self, "Choose a query image")
        if dlg.ShowModal() == wx.ID_OK:
            f = dlg.GetPath()
            dlg.Destroy()

            q = SimpleQuery(ImageReader([f]), ColorHistogram, ColorHistCorrel, self.db, HBase.TABLE_NAME)
            q.execute()
            for item in q.best_matches(5):
                print item

#######
# MAIN
#######
app = wx.App(False)
frame = MainWindow(None, "CBIR")
app.MainLoop()