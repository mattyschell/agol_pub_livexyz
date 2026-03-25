import base64
import json
import datetime


def _base64url_decode(input_str: str) -> bytes:
    padding = '=' * ((4 - len(input_str) % 4) % 4)
    return base64.urlsafe_b64decode(input_str + padding)


def is_jwt_token_expired(token) -> bool:
    current_time = datetime.datetime.utcnow()
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return True

        payload_b64 = parts[1]
        payload_bytes = _base64url_decode(payload_b64)
        payload = json.loads(payload_bytes.decode('utf-8'))

        if 'exp' not in payload:
            return True

        exp_timestamp = int(payload['exp'])
        exp_datetime = datetime.datetime.utcfromtimestamp(exp_timestamp)

        if exp_datetime < current_time - datetime.timedelta(minutes=1):
            return True  # Token has expired
        return False  # Token is still valid

    except Exception:
        return True  # Sometimes a decode error will occur
