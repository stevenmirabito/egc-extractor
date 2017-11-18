import wx
from wx.lib.filebrowsebutton import FileBrowseButton, DirBrowseButton
from wx.lib.agw.hyperlink import HyperLinkCtrl
from egc_extractor.gui import TitledPage


class WelcomePage(TitledPage):
    def __init__(self, parent, config):
        super(WelcomePage, self).__init__(parent, "Welcome!")

        self.config = config
        self.next_btn = self.FindWindowById(wx.ID_FORWARD)
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_update, self.timer)

        self.sizer.Add(wx.StaticText(self, -1, """This tool will help you extract electronic gift cards from
their delivery emails into a CSV file for further processing.

To get started, choose a location for the extracted card CSV:"""), 0, wx.ALL, 5)

        self.csv_path = FileBrowseButton(self, wx.ID_ANY, fileMode=wx.FD_SAVE,
                                         labelText="CSV Location:",
                                         fileMask="Comma Separated Value Files (*.csv)|*.csv",
                                         dialogTitle="Choose a CSV location")
        self.sizer.Add(self.csv_path, 0, wx.ALL | wx.EXPAND, 5)

        self.save_screenshot = wx.CheckBox(self, label="Save a screenshot for each card")
        self.save_screenshot.SetValue(True)
        self.sizer.Add(self.save_screenshot, 0, wx.ALL, 5)

        self.save_screenshot.Bind(wx.EVT_CHECKBOX, self.on_screenshot_selected)

        self.screenshot_directory = DirBrowseButton(self, wx.ID_ANY, labelText="Screenshots Directory:")
        self.sizer.Add(self.screenshot_directory, 0, wx.ALL | wx.EXPAND, 5)

        donate_text = wx.StaticText(self, -1, "Found this tool helpful?")
        donate_link = HyperLinkCtrl(self, -1, "Donate to the author", URL="https://stevenmirabito.com/kudos")
        donate_link_sizer = wx.BoxSizer(wx.HORIZONTAL)
        donate_link_sizer.Add(donate_text, 0, wx.LEFT, 5)
        donate_link_sizer.Add(donate_link, 0, wx.LEFT, 2)
        self.sizer.Add(donate_link_sizer)

    def on_screenshot_selected(self, event):
        if self.save_screenshot.GetValue():
            self.screenshot_directory.Show()
        else:
            self.screenshot_directory.Hide()

    def on_show(self):
        self.next_btn.Disable()
        self.timer.Start(1)

    def on_hide(self):
        self.timer.Stop()
        self.next_btn.Enable()

        self.config.set("paths", "csv", self.csv_path.GetValue(), persist=False)

        if self.save_screenshot.GetValue():
            self.config.set("paths", "screenshots", self.screenshot_directory.GetValue(), persist=False)

    def on_update(self, event):
        """
        Enables the Next button if all browse controls have paths
        """
        if self.csv_path.GetValue() and (
                self.screenshot_directory.GetValue() if self.save_screenshot.GetValue() else True):
            # Fields are filled, enable the button
            self.next_btn.Enable()
        elif self.next_btn.IsEnabled():
            # Fields are no longer filled, disable the button again
            self.next_btn.Disable()
