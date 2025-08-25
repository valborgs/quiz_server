from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .upbit_client import UpbitClient, MARKET

def _ok(data): return Response({"ok": True, "data": data})
def _err(code, message, http_status=status.HTTP_400_BAD_REQUEST):
    return Response({"ok": False, "error": {"code": code, "message": message}}, status=http_status)

@api_view(["GET"])
@permission_classes([AllowAny])
def get_eth_balance(request):
    client = UpbitClient()
    try:
        accounts = client.get_accounts()
        eth = next((a for a in accounts if a.get("currency") == "ETH"), None)
        ticker = client.get_ticker(MARKET)
    except Exception as e:
        return _err("UPBIT_ERROR", f"Upbit 호출 실패: {e}", status.HTTP_502_BAD_GATEWAY)

    trade_price = float(ticker.get("trade_price", 0) or 0)
    if not eth:
        return _ok({
            "currency": "ETH",
            "balance": "0",
            "locked": "0",
            "avg_buy_price": "0",
            "trade_price": trade_price,
            "valuation_krw": 0,
            "pnl_krw": 0,
            "pnl_rate": 0,
        })

    balance = float(eth.get("balance", 0) or 0)
    locked = float(eth.get("locked", 0) or 0)
    avg_buy_price = float(eth.get("avg_buy_price", 0) or 0)
    total_qty = balance + locked
    valuation_krw = round(total_qty * trade_price)
    pnl_krw = round(total_qty * (trade_price - avg_buy_price))
    pnl_rate = round(((trade_price / avg_buy_price) - 1) * 100, 4) if avg_buy_price > 0 else 0.0

    return _ok({
        "currency": "ETH",
        "balance": eth.get("balance"),
        "locked": eth.get("locked"),
        "avg_buy_price": eth.get("avg_buy_price"),
        "unit_currency": eth.get("unit_currency"),
        "trade_price": trade_price,
        "valuation_krw": valuation_krw,
        "pnl_krw": pnl_krw,
        "pnl_rate": pnl_rate,
    })

@api_view(["GET"])
@permission_classes([AllowAny])
def get_eth_ticker(request):
    client = UpbitClient()
    try:
        data = client.get_ticker(MARKET)
    except Exception as e:
        return _err("UPBIT_ERROR", f"Upbit 호출 실패: {e}", status.HTTP_502_BAD_GATEWAY)
    return _ok(data)

@api_view(["POST"])
@permission_classes([AllowAny])
def post_market_buy(request):
    krw_amount = int(request.data.get("krw_amount", 0))
    if krw_amount < 5000:
        return _err("INVALID_AMOUNT", "최소 주문 금액은 5,000 KRW 입니다.")
    identifier = request.data.get("client_id")
    payload = {
        "market": MARKET,
        "side": "bid",
        "ord_type": "price",
        "price": str(krw_amount),
    }
    if identifier:
        payload["identifier"] = identifier

    client = UpbitClient()
    try:
        data = client.create_order(payload)
        return _ok(data)
    except Exception as e:
        return _err("UPBIT_ERROR", f"주문 실패: {e}", status.HTTP_502_BAD_GATEWAY)

@api_view(["POST"])
@permission_classes([AllowAny])
def post_market_sell(request):
    volume = str(request.data.get("volume", "")).strip()
    if not volume:
        return _err("INVALID_VOLUME", "매도 수량(volume)은 필수입니다.")
    identifier = request.data.get("client_id")
    payload = {
        "market": MARKET,
        "side": "ask",
        "ord_type": "market",
        "volume": volume,
    }
    if identifier:
        payload["identifier"] = identifier

    client = UpbitClient()
    try:
        data = client.create_order(payload)
        return _ok(data)
    except Exception as e:
        return _err("UPBIT_ERROR", f"주문 실패: {e}", status.HTTP_502_BAD_GATEWAY)

@api_view(["POST"])
@permission_classes([AllowAny])
def post_cancel_order(request):
    uuid = request.data.get("uuid")
    identifier = request.data.get("identifier")
    if not uuid and not identifier:
        return _err("INVALID_PARAMS", "uuid 또는 identifier 중 하나는 필수입니다.")
    client = UpbitClient()
    try:
        data = client.cancel_order(uuid=uuid, identifier=identifier)
        return _ok(data)
    except Exception as e:
        return _err("UPBIT_ERROR", f"취소 실패: {e}", status.HTTP_502_BAD_GATEWAY)

@api_view(["POST"])
@permission_classes([AllowAny])
def post_cancel_and_new(request):
    payload = {
        "prev_uuid": request.data.get("prev_uuid"),
        "prev_identifier": request.data.get("prev_identifier"),
        "new_ord_type": request.data.get("new_ord_type"),
        "new_volume": request.data.get("new_volume"),
        "new_price": request.data.get("new_price"),
        "new_time_in_force": request.data.get("new_time_in_force"),
        "new_smp_type": request.data.get("new_smp_type"),
        "new_identifier": request.data.get("new_identifier"),
    }
    payload = {k: v for k, v in payload.items() if v not in (None, "")}

    client = UpbitClient()
    try:
        data = client.cancel_and_new(payload)
        return _ok(data)
    except Exception as e:
        return _err("UPBIT_ERROR", f"취소 후 재주문 실패: {e}", status.HTTP_502_BAD_GATEWAY)