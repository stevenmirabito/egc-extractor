from egc_extractor.plugin import register
from egc_extractor.plugin import MerchantPlugin


@register
class PayPalDigitalGifts(MerchantPlugin):
    display_name = "PayPal Digital Gifts"
    from_email = "gifts@paypal.com"
