from egc_extractor.plugin import register
from egc_extractor.plugin import MerchantPlugin


@register
class Cashstar(MerchantPlugin):
    display_name = "Cashstar"
    from_email = "[merchantname]giftcards@cashstar.com"
