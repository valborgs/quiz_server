from django.urls import path
from . import views

urlpatterns = [
    path("balances/eth", views.get_eth_balance),
    path("ticker/eth", views.get_eth_ticker),
    path("orders/eth/market-buy", views.post_market_buy),
    path("orders/eth/market-sell", views.post_market_sell),
    path("orders/cancel", views.post_cancel_order),
    path("orders/cancel-and-new", views.post_cancel_and_new),
]