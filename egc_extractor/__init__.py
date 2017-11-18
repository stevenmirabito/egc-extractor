import wx
from wx.adv import Wizard
import egc_extractor.merchants
from egc_extractor.config import Configuration
from egc_extractor.util import get_resource_path
from egc_extractor.plugin import discover_plugins
from egc_extractor.wizard.welcome import WelcomePage
from egc_extractor.wizard.merchant import MerchantChooserPage
from egc_extractor.wizard.email import EmailConnectionPage
from egc_extractor.wizard.options import OptionsPage
from egc_extractor.wizard.progress import ProgressPage


class ExtractorWizard(Wizard):
    def __init__(self, config, merchants):
        sidebar_bitmap = wx.Bitmap(get_resource_path('wizard_sidebar.png'))
        super(ExtractorWizard, self).__init__(None, -1, "Universal eGC Extractor", sidebar_bitmap)

        self.Bind(wx.adv.EVT_WIZARD_PAGE_CHANGED, self.on_page_changed)
        self.Bind(wx.adv.EVT_WIZARD_PAGE_CHANGING, self.on_page_changing)

        page1 = WelcomePage(self)
        page2 = EmailConnectionPage(self, config)
        page3 = MerchantChooserPage(self, config, merchants)
        page4 = OptionsPage(self, config, merchants)
        page5 = ProgressPage(self, config, merchants)

        # Configure the page order
        page1.SetNext(page2)
        page2.SetPrev(page1)
        page2.SetNext(page3)
        page3.SetPrev(page2)
        page3.SetNext(page4)
        page4.SetPrev(page3)
        page4.SetNext(page5)

        self.FitToPage(page1)
        self.GetPageAreaSizer().Add(page1)
        self.RunWizard(page1)
        self.Destroy()

    @staticmethod
    def on_page_changed(event):
        page = event.GetPage()
        hook = getattr(page, "on_show", None)

        if callable(hook):
            hook()

    @staticmethod
    def on_page_changing(event):
        page = event.GetPage()
        hook = getattr(page, "on_hide", None)

        if callable(hook):
            hook()


def main():
    # Load configuration
    config = Configuration()

    # Discover merchant plugins
    merchant_plugins = discover_plugins(egc_extractor.merchants)

    app = wx.App()
    ExtractorWizard(config, merchant_plugins)
    app.MainLoop()
