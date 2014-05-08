import ConfigParser
import inspect
import sys
import wx
from os import path
from os import listdir
from string import split
from src.descriptors import *
from src.comparators import *
from src.query.SimpleQuery import SimpleQuery
from src.readers.ImageReader import ImageReader
from src.ui.ResultPresenter import ImagePresenter

__author__ = 'Rigi'


ID_CONSOLE_WINDOW = 5000
ID_QUERY_WINDOW = 5001

ID_REF = 5010
ID_DAT = 5011
ID_EXT = 5012
ID_CMP = 5013
ID_QRY = 5014

URL_REFERENCE = "url_reference"
URL_DATABASE = "url_reference"
URL_EXTRACT = "url_extract"
URL_COMPARE = "url_compare"
URL_QUERY = "url_query"


class MainWindow(wx.MDIParentFrame):
    config = ConfigParser.SafeConfigParser({"host": "localhost", "port": "9090"})
    config.read(path.join(path.dirname(__file__), "../myconfig.cfg"))

    # Constructor
    def __init__(self, parent, title):
        wx.MDIParentFrame.__init__(self, parent, title=title, size=(800, 600))

        self.query = SimpleQuery()

        # A status bar in the bottom of the window
        self.sb = self.CreateStatusBar()

        # File menu
        file_menu = wx.Menu()
        self.Bind(wx.EVT_MENU, self.OnOpenQuery,
                  file_menu.Append(wx.ID_OPEN, "&Open Query...", " Open a Simple Query"))
        self.Bind(wx.EVT_MENU, self.OnCreateQuery,
                  file_menu.Append(wx.ID_NEW, "&Create New Query", " Create a Simple Query"))
        self.Bind(wx.EVT_MENU, self.OnCreateQuery,
                  file_menu.Append(wx.ID_CLOSE, "&Close Query", " Close active query"))
        file_menu.AppendSeparator()
        self.Bind(wx.EVT_MENU, self.OnSaveQuery,
                  file_menu.Append(wx.ID_SAVE, "&Save Query", " Save a Simple Query"))
        self.Bind(wx.EVT_MENU, self.OnSaveQuery,
                  file_menu.Append(wx.ID_SAVEAS, "&Save Query As...", " Save a Simple Query as..."))
        file_menu.AppendSeparator()
        self.Bind(wx.EVT_MENU, self.OnExit,
                  file_menu.Append(wx.ID_EXIT, "E&xit", " Terminate the program"))

        # Database menu
        db_menu = wx.Menu()
        self.Bind(wx.EVT_MENU, self.OnRecreateTable,
                  db_menu.Append(wx.ID_DELETE, "&Recreate Table", " Delete and recreate the CBIR table of selected database"))
        self.Bind(wx.EVT_MENU, self.OnFixTable,
                  db_menu.Append(wx.ID_REMOVE, "&Fix Table", " Remove invalid file references from selected database"))
        self.Bind(wx.EVT_MENU, self.OnUploadImages,
                  db_menu.Append(wx.ID_ADD, "&Upload Images", " Upload images from local directory"))

        # Creating the menu bar.
        menu_bar = wx.MenuBar()
        menu_bar.Append(file_menu, "&File")
        menu_bar.Append(db_menu, "&Database")
        self.SetMenuBar(menu_bar)

        win = wx.SashLayoutWindow(self, ID_CONSOLE_WINDOW, style=wx.NO_BORDER | wx.SW_3D)
        win.SetDefaultSize((1000, 100))
        win.SetOrientation(wx.LAYOUT_HORIZONTAL)
        win.SetAlignment(wx.LAYOUT_BOTTOM)
        win.SetBackgroundColour(wx.Colour(0, 0, 0))
        win.SetSashVisible(wx.SASH_TOP, False)
        self.consoleTextBox = wx.TextCtrl(win, style=wx.TE_MULTILINE | wx.SUNKEN_BORDER)
        self.consoleTextBox.SetBackgroundColour(wx.Colour(0, 0, 0))
        self.consoleTextBox.SetForegroundColour(wx.Colour(0, 255, 0))

        win = wx.SashLayoutWindow(self, ID_QUERY_WINDOW, style=wx.NO_BORDER | wx.SW_3D)
        win.SetDefaultSize((200, 1000))
        win.SetOrientation(wx.LAYOUT_VERTICAL)
        win.SetAlignment(wx.LAYOUT_RIGHT)
        win.SetBackgroundColour(wx.Colour(255, 255, 255))
        win.SetSashVisible(wx.SASH_LEFT, False)
        p = wx.Panel(win)
        hbox = wx.BoxSizer(wx.VERTICAL)
        hbox.Add(wx.HyperlinkCtrl(p, ID_REF, label="Reference: None", url=URL_REFERENCE), 1, wx.EXPAND)
        hbox.Add(wx.HyperlinkCtrl(p, ID_DAT, label="Database: None", url=URL_DATABASE), 1, wx.EXPAND)
        hbox.Add(wx.HyperlinkCtrl(p, ID_EXT, label="Extract: None", url=URL_EXTRACT), 1, wx.EXPAND)
        hbox.Add(wx.HyperlinkCtrl(p, ID_CMP, label="Compare: None", url=URL_COMPARE), 1, wx.EXPAND)
        hbox.Add(wx.HyperlinkCtrl(p, ID_QRY, label="Query: None", url=URL_QUERY), 1, wx.EXPAND)
        btn = wx.Button(p, label="Retrieve!")
        hbox.Add(btn, 1, wx.EXPAND)
        p.SetSizer(hbox)
        self.wndQuery = win

        self.Bind(wx.EVT_BUTTON, self.OnRetrieveImages, btn)
        self.Bind(wx.EVT_HYPERLINK, self.OnLinkClick)
        self.Bind(wx.EVT_SIZE, self.OnSize)

        # Set the window position and visibility
        self.Centre()
        self.Show()

    def PrintConsole(self, text):
        self.consoleTextBox.AppendText(text + "\n")

    def OnSize(self, e):
        wx.LayoutAlgorithm().LayoutMDIFrame(self)
        self.Refresh()

    def OnExit(self, e):
        self.query.kill()
        self.Close(True)

    def OnLinkClick(self, e):
        if e.GetId() == ID_REF:
            self.OnChangeReference()
        elif e.GetId() == ID_DAT:
            self.OnChangeDatabase()
        elif e.GetId() == ID_EXT:
            self.OnChangeExtractor()
        elif e.GetId() == ID_CMP:
            self.OnChangeComparator()
        elif e.GetId() == ID_QRY:
            self.OnChangeQueryImage()

    def OnRetrieveImages(self, e):
        self.query.execute()
        child = wx.MDIChildFrame(self)
        img = ImagePresenter(self.query.best_matches(5), child)
        img.Show()
        child.Show()

    def OnChangeReference(self):
        dlg = wx.DirDialog(self, "Open the reference images directory")
        if dlg.ShowModal() == wx.ID_OK:
            images = [path.join(dlg.GetPath(), f) for f in listdir(dlg.GetPath())]
            self.query.reference_images = ImageReader(images)
            self.wndQuery.FindWindowById(ID_REF).SetLabel("Reference: " + dlg.GetPath())
            self.PrintConsole("Reference images directory set to " + dlg.GetPath())
        dlg.Destroy()

    def OnChangeDatabase(self):
        dlg = wx.TextEntryDialog(self, "Enter Image Database URL", "Add Image Database", defaultValue=self.config.get("database", "host") + ':' + self.config.get("database", "port"))
        if dlg.ShowModal() == wx.ID_OK:
            try:
                v = split(dlg.GetValue(), ':', 2)
                self.query.set_database(v)
                self.wndQuery.FindWindowById(ID_DAT).SetLabel("Database: " + dlg.GetValue())
                self.PrintConsole("Database changed to " + dlg.GetValue())
            except:
                self.PrintConsole("Failed to change database!")
        dlg.Destroy()

    def OnChangeExtractor(self):
        extractors = [[], []]
        for mname, mvalue in inspect.getmembers(sys.modules["src.descriptors"], inspect.ismodule):
            for cname, cvalue in inspect.getmembers(mvalue, inspect.isclass):
                if not inspect.isabstract(cvalue) and issubclass(cvalue, abstractdesc.AbstractDescriptor):
                    extractors[0].append(cname)
                    extractors[1].append(cvalue)
        dlg = wx.SingleChoiceDialog(self, "Choose the feature extractor class", "Add Feature Extractor", extractors[0])
        if dlg.ShowModal() == wx.ID_OK:
            try:
                self.query.descriptor_cls = extractors[1][dlg.GetSelection()]
                self.wndQuery.FindWindowById(ID_EXT).SetLabel("Extract: " + extractors[0][dlg.GetSelection()])
                self.PrintConsole("Feature extractor changed to " + extractors[0][dlg.GetSelection()])
            except:
                self.PrintConsole("Failed to change feature extractor")
        dlg.Destroy()


    def OnChangeComparator(self):
        if self.query.descriptor_cls:
            comparators = [[], []]
            for mname, mvalue in inspect.getmembers(sys.modules["src.comparators"], inspect.ismodule):
                for cname, cvalue in inspect.getmembers(mvalue, inspect.isclass):
                    if not inspect.isabstract(cvalue) and issubclass(cvalue, AbstractComparator.AbstractComparator) and cvalue.is_acceptable(self.query.descriptor_cls):
                        comparators[0].append(cname)
                        comparators[1].append(cvalue)
            dlg = wx.SingleChoiceDialog(self, "Choose the comparator class", "Add Comparator", comparators[0])
            if dlg.ShowModal() == wx.ID_OK:
                try:
                    self.query.comparator_cls = comparators[1][dlg.GetSelection()]
                    self.wndQuery.FindWindowById(ID_CMP).SetLabel("Compare: " + comparators[0][dlg.GetSelection()])
                    self.PrintConsole("Comparator changed to " + comparators[0][dlg.GetSelection()])
                except:
                    self.PrintConsole("Failed to change comparator")
            dlg.Destroy()
        else:
            wx.MessageBox("Choose feature extractor first!", "Comparator change failed")

    def OnChangeQueryImage(self):
        dlg = wx.FileDialog(self, "Open a query file")
        if dlg.ShowModal() == wx.ID_OK:
            self.query.query_image = ImageReader([dlg.GetPath()])
            self.wndQuery.FindWindowById(ID_QRY).SetLabel("Query: " + dlg.GetPath())
            self.PrintConsole("Query image path set to " + dlg.GetPath())
        dlg.Destroy()

    def OnQueryChanged(self):
        db = self.query.get_database()
        self.wndQuery.FindWindowById(ID_REF).SetLabel("Reference: " + db[0] + ":" + db[1])
        self.wndQuery.FindWindowById(ID_EXT).SetLabel("Extract: " + self.query.descriptor_cls.__name__)
        self.wndQuery.FindWindowById(ID_CMP).SetLabel("Compare: " + self.query.comparator_cls.__name__)
        self.wndQuery.FindWindowById(ID_QRY).SetLabel("Query: " + self.query.query_image.paths[0])
        self.PrintConsole("Query reinitialized!")

    def OnSaveQuery(self, e):
        if e.GetId() == wx.ID_SAVEAS or not self.query.issaved():
            dlg = wx.FileDialog(self, style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
            if dlg.ShowModal() == wx.ID_OK:
                self.query.save(dlg.GetPath())
                dlg.Destroy()
        else:
            self.query.save()

    def OnOpenQuery(self, e):
        dlg = wx.FileDialog(self, "Open a query file")
        if dlg.ShowModal() == wx.ID_OK:
            self.query.kill()
            self.query = SimpleQuery()
            self.query.open(dlg.GetPath())
            self.OnQueryChanged()
        dlg.Destroy()

    def OnCreateQuery(self, e):
        self.query.kill()
        self.query = SimpleQuery()
        self.OnQueryChanged()

    def OnRecreateTable(self, e):
        if self.query.database:
            self.query.database.deleteTable()
            self.PrintConsole("Table dropped.")
            self.query.database.createTable()
            self.PrintConsole("Table created.")
        else:
            self.PrintConsole("No database selected!")

    def OnFixTable(self, e):
        if self.query.database:
            self.query.database.removeInvalidImages()
            self.PrintConsole("Invalid file references removed.")
        else:
            self.PrintConsole("No database selected!")

    def OnUploadImages(self, e):
        if self.query.database:
            dlg = wx.DirDialog(self, "Select the image directory")
            if dlg.ShowModal() == wx.ID_OK:
                images = [path.join(dlg.GetPath(), f) for f in listdir(dlg.GetPath())]
                self.query.database.uploadImages(images)
            dlg.Destroy()
        else:
            self.PrintConsole("No database selected!")

#######
# MAIN
#######
app = wx.App(False)
frame = MainWindow(None, "CBIR")
app.MainLoop()