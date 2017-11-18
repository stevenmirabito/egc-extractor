from egc_extractor.plugin import register
from egc_extractor.plugin import MerchantPlugin


@register
class Staples(MerchantPlugin):
    display_name = "Staples"
    default_from_email = "DoNotReply.Staples@blackhawk-net.com"
