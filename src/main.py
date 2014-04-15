__author__ = 'Rigi'

import os, cv2, wx
from hbase import HBase
from numpy import *

class MainWindow(wx.Frame):
    client = HBase("http://localhost:8080")
    tablename = "cbir"
    columnfamily = "feature"

    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(200,100))

        # Create table if necessary
        r = self.client.listTable()
        if self.tablename not in r.content:
            r = self.client.createTable(self.tablename, self.columnfamily)

        # A Statusbar in the bottom of the window
        r = self.client.getVersion()
        self.CreateStatusBar().SetStatusText("HBase version is " + r.content + " at localhost:8080", 0)

        # Setting up the menu.
        filemenu = wx.Menu()

        # wx.ID_ABOUT and wx.ID_EXIT are standard IDs provided by wxWidgets.
        self.Bind(wx.EVT_MENU, self.OnOpen,
                  filemenu.Append(wx.ID_OPEN, "&Open", ""))
        self.Bind(wx.EVT_MENU, self.OnAbout,
                  filemenu.Append(wx.ID_ABOUT, "&About", " Information about this program"))
        filemenu.AppendSeparator()
        self.Bind(wx.EVT_MENU, self.OnExit,
                  filemenu.Append(wx.ID_EXIT, "E&xit", " Terminate the program"))

        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu, "&File") # Adding the "filemenu" to the MenuBar
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.
        self.Show(True)

    def OnAbout(self, e):
        # A message dialog box with an OK button. wx.OK is a standard ID in wxWidgets.
        dlg = wx.MessageDialog(self, "A small text editor", "About Sample Editor", wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

    def OnExit(self, e):
        self.Close(True)  # Close the frame.

    def OnOpen(self, e):
        """ Open a file"""
        self.dirname = ''
        dlg = wx.DirDialog(self, "Choose a image directory")
        if dlg.ShowModal() == wx.ID_OK:
            self.dirname = dlg.GetPath()
            self.targetdir = dlg.GetPath() + "/target"
            for fname in os.listdir(self.dirname):
                img = cv2.imread(os.path.join(self.dirname, fname))
                h0 = cv2.calcHist([img], [0], None, [64], [0, 256])
                cv2.normalize(h0, h0, 0, 255, cv2.NORM_MINMAX)
                h1 = cv2.calcHist([img], [1], None, [64], [0, 256])
                cv2.normalize(h1, h1, 0, 255, cv2.NORM_MINMAX)
                h2 = cv2.calcHist([img], [2], None, [64], [0, 256])
                cv2.normalize(h2, h2, 0, 255, cv2.NORM_MINMAX)

                self.client.putValue(self.tablename, fname, self.columnfamily + ":color_hist", h0)

                print fname
                print [h0, h1, h2]

        dlg.Destroy()




app = wx.App(False)
frame = MainWindow(None, "Sample editor")
app.MainLoop()