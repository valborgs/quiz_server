import uuid
import hashlib
import jwt
from typing import Mapping, Optional
from urllib.parse import urlencode, unquote

def build_query_string(params: Optional[Mapping]) -> str:
    if not params:
        return ""
    # Upbit 규칙: URL 인코딩되지 않은 쿼리 문자열을 SHA512로 해시
    return unquote(urlencode(params, doseq=True))

def make_jwt(access_key: str, secret_key: str, query_string: str = "") -> str:
    payload = {
        "access_key": access_key,
        "nonce": str(uuid.uuid4()),
    }
    if query_string:
        payload["query_hash"] = hashlib.sha512(query_string.encode("utf-8")).hexdigest()
        payload["query_hash_alg"] = "SHA512"
    token = jwt.encode(payload, secret_key, algorithm="HS512")
    return token if isinstance(token, str) else token.decode("utf-8")