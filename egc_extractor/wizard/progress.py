import logging
import wx
from egc_extractor.gui import TitledPage, TextCtrlHandler
from egc_extractor.extract import extract


class ProgressPage(TitledPage):
    def __init__(self, parent, config, merchants):
        super(ProgressPage, self).__init__(parent, "Extracting...")

        self.config = config
        self.merchants = merchants
        self.prompt = wx.StaticText(self, -1, "This may take a few minutes. Please don't touch your keyboard or mouse.")
        self.sizer.Add(self.prompt, 0, wx.ALL, 5)

        self.progress = wx.Gauge(self)
        self.progress.Pulse()
        self.sizer.Add(self.progress, 0, wx.ALL | wx.EXPAND, 15)

        self.log = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY, size=(250, 200))
        self.sizer.Add(self.log, 0, wx.ALL | wx.EXPAND, 15)

        self.logger = logging.getLogger()
        text_handler = TextCtrlHandler(self.log)
        self.logger.addHandler(text_handler)

    def on_show(self):
        next_btn = self.FindWindowById(wx.ID_FORWARD)
        next_btn.Disable()

        merchant = self.merchants[int(self.config.get("options", "merchant"))]
        if extract(self.config, merchant, self.progress, self.logger):
            self.set_title("Extraction Complete")
        else:
            self.set_title("Extraction Failed")

        self.prompt.SetLabel("Review the log below, then click Next to continue.")
        self.progress.SetValue(100)
        next_btn.Enable()
