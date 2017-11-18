import logging
import wx.adv
from wx.adv import WizardPageSimple


class TitledPage(WizardPageSimple):
    def __init__(self, parent, title):
        WizardPageSimple.__init__(self, parent)

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer = sizer
        self.SetSizer(sizer)
        title = wx.StaticText(self, -1, title)
        self.title = title
        title.SetFont(wx.Font(16, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.sizer.Add(title, 0, wx.ALIGN_LEFT | wx.ALL, 5)
        self.sizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND | wx.ALL, 5)

    def set_title(self, title):
        self.title.SetLabel(title)


class TextCtrlHandler(logging.Handler):
    def __init__(self, text):
        logging.Handler.__init__(self)
        self.text = text

    def emit(self, record):
        msg = self.format(record)
        self.text.AppendText(msg + "\n")
