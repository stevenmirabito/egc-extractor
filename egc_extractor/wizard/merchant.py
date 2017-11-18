import wx
from egc_extractor.gui import TitledPage


class MerchantChooserPage(TitledPage):
    def __init__(self, parent, config, merchants):
        super(MerchantChooserPage, self).__init__(parent, "Merchant")

        self.config = config
        prompt = wx.StaticText(self, -1, "Where did you purchase the cards you would like to extract?")
        self.sizer.Add(prompt, 0, wx.ALL, 5)

        merchant_choices = [merchant.display_name for merchant in merchants]
        self.chooser = wx.RadioBox(self, choices=merchant_choices, majorDimension=1, style=wx.RA_SPECIFY_COLS)
        self.sizer.Add(self.chooser, 0, wx.EXPAND | wx.ALIGN_LEFT)

    def on_hide(self):
        self.config.set("options", "merchant", self.chooser.GetSelection(), persist=False)
