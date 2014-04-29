import wx

__author__ = 'Rigi'


class QueryUI(wx.MDIChildFrame):

    def __init__(self, parent, title):
        wx.MDIChildFrame.__init__(self, parent, title=title)

        # Command menu
        cmd_menu = wx.Menu()
        self.Bind(wx.EVT_MENU, self.OnRecalcHist,
                  cmd_menu.Append(wx.ID_ANY, "&Histogram", " Recalc Color Histogram Features" + title))

        # Query menu
        qry_menu = wx.Menu()
        self.Bind(wx.EVT_MENU, self.OnQueryColorHist,
                  qry_menu.Append(wx.ID_ANY, "&Histogram", " Retrieve images via Color Histogram Features"))

        # Creating the menu bar.
        menu_bar = wx.MenuBar()
        menu_bar.Append(cmd_menu, "&Extract Features")
        menu_bar.Append(qry_menu, "&Query By")
        self.SetMenuBar(menu_bar)

    def OnRecalcHist(self):
        pass

    def OnQueryColorHist(self):
        pass