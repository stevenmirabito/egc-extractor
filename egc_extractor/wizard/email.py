import wx
from egc_extractor.gui import TitledPage


class EmailConnectionPage(TitledPage):
    def __init__(self, parent, config):
        super(EmailConnectionPage, self).__init__(parent, "Email Account")

        self.config = config
        self.next_btn = self.FindWindowById(wx.ID_FORWARD)
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_update, self.timer)

        prompt = wx.StaticText(self, -1, "To retrieve your card delivery emails, enter the following information:")
        self.sizer.Add(prompt, 0, wx.ALL, 5)

        label_mail_server = wx.StaticText(self, label="Mail Server:")
        label_port = wx.StaticText(self, label="Port:")
        label_ssl = wx.StaticText(self, label="SSL:")
        label_username = wx.StaticText(self, label="User Name:")
        label_password = wx.StaticText(self, label="Password:")

        self.hostname = wx.TextCtrl(self, value=config.get("email", "hostname"))
        self.port = wx.TextCtrl(self, value=str(config.get("email", "port")))
        self.ssl = wx.CheckBox(self)
        if config.get("email", "ssl").lower() == "true":
            self.ssl.SetValue(True)
        self.username = wx.TextCtrl(self, value=config.get("email", "username"))
        self.password = wx.TextCtrl(self, value=config.get("email", "password"), style=wx.TE_PASSWORD)

        form = wx.FlexGridSizer(5, 2, 9, 25)

        form.AddMany([
            label_mail_server, (self.hostname, 1, wx.EXPAND),
            label_port, (self.port, 1, wx.EXPAND),
            label_ssl, (self.ssl, 1, wx.EXPAND),
            label_username, (self.username, 1, wx.EXPAND),
            label_password, (self.password, 1, wx.EXPAND)
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
        self.next_btn.Disable()
        self.timer.Start(1)

    def on_hide(self):
        self.timer.Stop()
        self.next_btn.Enable()

        persist = self.remember.GetValue()
        self.config.set("email", "hostname", self.hostname.GetValue(), persist=persist)
        self.config.set("email", "port", self.port.GetValue(), persist=persist)
        self.config.set("email", "ssl", self.ssl.GetValue(), persist=persist)
        self.config.set("email", "username", self.username.GetValue(), persist=persist)
        self.config.set("email", "password", self.password.GetValue(), persist=persist)

        if persist:
            self.config.commit()

    def on_update(self, _):
        """
        Enables the Next button if all text controls have values
        """
        if self.hostname.GetValue() and \
                self.port.GetValue() and \
                self.username.GetValue() and \
                self.password.GetValue():
            # Fields are filled, enable the button
            self.next_btn.Enable()
        elif self.next_btn.IsEnabled():
            # Fields are no longer filled, disable the button again
            self.next_btn.Disable()
