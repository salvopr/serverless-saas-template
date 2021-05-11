from unittest.mock import patch, MagicMock

from app.payments.plans import get_prices_from_stripe


def test_get_prices_from_stripe(stripe_plans):
    assert get_prices_from_stripe() == [{'price_id': 'priceid1', 'product_id': 'productid1', 'product_name': 'product_name', 'amount': 500, 'currency': 'eur', 'interval': 'month'}, {'price_id': 'priceid2', 'product_id': 'productid2', 'product_name': 'product_name', 'amount': 1000, 'currency': 'eur', 'interval': 'year'}]
