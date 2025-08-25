import httpx
from typing import Any, Dict, Optional
from django.conf import settings
from .signing import build_query_string, make_jwt

UPBIT_BASE_URL = "https://api.upbit.com"
MARKET = "KRW-ETH"

class UpbitClient:
    def __init__(self, access_key: Optional[str] = None, secret_key: Optional[str] = None):
        self.access_key = access_key or settings.UPBIT_ACCESS_KEY
        self.secret_key = secret_key or settings.UPBIT_SECRET_KEY
        self.client = httpx.Client(base_url=UPBIT_BASE_URL, timeout=httpx.Timeout(10.0, read=15.0))

    # --- Public (no auth)
    def get_ticker(self, market: str = MARKET):
        r = self.client.get("/v1/ticker", params={"markets": market})
        r.raise_for_status()
        arr = r.json()
        return arr[0] if isinstance(arr, list) and arr else arr

    # --- Private (auth)
    def _auth_headers(self, method: str, *, params: Optional[Dict[str, Any]] = None, json_body: Optional[Dict[str, Any]] = None):
        qs = ""
        if method in ("GET", "DELETE"):
            qs = build_query_string(params)
        elif method == "POST":
            qs = build_query_string(json_body)
        token = make_jwt(self.access_key, self.secret_key, qs)
        return {"Authorization": f"Bearer {token}"}

    def get_accounts(self):
        headers = self._auth_headers("GET")
        r = self.client.get("/v1/accounts", headers=headers)
        r.raise_for_status()
        return r.json()

    def create_order(self, payload: Dict[str, Any]):
        headers = self._auth_headers("POST", json_body=payload)
        r = self.client.post("/v1/orders", headers=headers, json=payload)
        r.raise_for_status()
        return r.json()

    def cancel_order(self, *, uuid: Optional[str] = None, identifier: Optional[str] = None):
        params = {}
        if uuid:
            params["uuid"] = uuid
        if identifier:
            params["identifier"] = identifier
        headers = self._auth_headers("DELETE", params=params)
        r = self.client.delete("/v1/order", headers=headers, params=params)
        r.raise_for_status()
        return r.json()

    def cancel_and_new(self, payload: Dict[str, Any]):
        headers = self._auth_headers("POST", json_body=payload)
        r = self.client.post("/v1/orders/cancel_and_new", headers=headers, json=payload)
        r.raise_for_status()
        return r.json()