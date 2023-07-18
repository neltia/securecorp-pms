from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.crypto import salted_hmac
from django.utils import timezone
from estimate.utils import encrypt_urlsafe


class CustomTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, email, timestamp):
        return str(email) + str(timestamp)

    def _make_token(self, email, timestamp):
        timestamp_bytes = str(timestamp).encode('utf-8')
        timestamp_base36 = encrypt_urlsafe.encode(timestamp_bytes)
        token = salted_hmac(
            self.key_salt,
            self._make_hash_value(email, timestamp),
            secret=self.secret,
        ).hexdigest()[::2]
        return f"{timestamp_base36}-{token}"


# gen token
def generate_token(email):
    timestamp = timezone.now().timestamp()
    token_generator = CustomTokenGenerator()
    token = token_generator._make_token(email, timestamp)
    return token


# token expire check
def is_expire_token(token, expire_hour):
    token_created_at = token.split("-")[0]
    created_timestamp = float(encrypt_urlsafe.decode(token_created_at))
    current_timestamp = timezone.now().timestamp()
    expires_timestamp = created_timestamp + 3600 * expire_hour
    if current_timestamp > expires_timestamp:
        return True
    return False
