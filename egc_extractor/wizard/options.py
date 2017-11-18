import wx
from egc_extractor.gui import TitledPage


class OptionsPage(TitledPage):
    def __init__(self, parent, config, merchants):
        super(OptionsPage, self).__init__(parent, "Additional Options")

        self.config = config
        self.merchants = merchants

        prompt = wx.StaticText(self, -1, "Adjust the following options to change the email scanning scope:")
        self.sizer.Add(prompt, 0, wx.ALL, 5)

        label_folder = wx.StaticText(self, label="Folder:")
        label_to = wx.StaticText(self, label="To Email:")
        label_from = wx.StaticText(self, label="From Email:")

        self.folder = wx.TextCtrl(self, value=config.get("options", "folder"))
        self.to_email = wx.TextCtrl(self, value=config.get("options", "to_email"))
        self.from_email = wx.TextCtrl(self)

        form = wx.FlexGridSizer(3, 2, 9, 25)

        form.AddMany([
            label_folder, (self.folder, 1, wx.EXPAND),
            label_to, (self.to_email, 1, wx.EXPAND),
            label_from, (self.from_email, 1, wx.EXPAND)
        ])

        form.AddGrowableCol(1, 1)

        self.sizer.Add(form, proportion=1, flag=wx.ALL | wx.EXPAND, border=15)

        label_remember = wx.StaticText(self, label="Remember these settings")
        self.remember = wx.CheckBox(self)
        self.remember.SetValue(True)
        remember_sizer = wx.BoxSizer(wx.HORIZONTAL)
        remember_sizer.AddMany([label_remember, self.remember])
        self.sizer.Add(remember_sizer)

    def on_show(self):
        self.from_email.SetValue(self.merchants[int(self.config.get("options", "merchant"))].from_email)

    def on_hide(self):
        persist = self.remember.GetValue()
        self.config.set("options", "folder", self.folder.GetValue(), persist=persist)
        self.config.set("options", "to_email", self.to_email.GetValue(), persist=persist)
        self.config.set("options", "from_email", self.from_email.GetValue(), persist=False)

        if persist:
            self.config.commit()
