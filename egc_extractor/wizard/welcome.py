import wx
from wx.lib.agw.hyperlink import HyperLinkCtrl
from egc_extractor.gui import TitledPage


class WelcomePage(TitledPage):
    def __init__(self, parent):
        super(WelcomePage, self).__init__(parent, "Welcome!")
        self.sizer.Add(wx.StaticText(self, -1, """This tool will help you extract electronic gift cards from
their delivery emails into a CSV file for further processing.

To get started, click Next.
"""), 0, wx.ALL, 5)

        donate_text = wx.StaticText(self, -1, "Found this tool helpful?")
        donate_link = HyperLinkCtrl(self, -1, "Donate to the author", URL="https://stevenmirabito.com/kudos")
        donate_link_sizer = wx.BoxSizer(wx.HORIZONTAL)
        donate_link_sizer.Add(donate_text, 0, wx.LEFT, 5)
        donate_link_sizer.Add(donate_link, 0, wx.LEFT, 2)
        self.sizer.Add(donate_link_sizer)
