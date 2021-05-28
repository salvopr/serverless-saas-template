from cachetools.func import ttl_cache
import stripe

from config import current_config
TRIAL_DAYS = 7


@ttl_cache(ttl=600)
def get_prices_from_stripe():
    # Only 1-year and 1-month intervals are supported
    stripe.api_key = current_config.STRIPE_SEC_KEY
    prices = []
    for price in stripe.Price.list():
        if price['active'] and price['recurring']:
            prices.append({"price_id": price["id"],
                           "product_id": price["product"],
                           "product_name": stripe.Product.retrieve(price["product"])["name"],
                           "amount": price["unit_amount"],
                           "currency": price["currency"],
                           "interval": price["recurring"]["interval"]})
    return prices
