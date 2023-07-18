from django.core.cache import cache
from datetime import datetime
import hashlib


def email_limit_chk(to_email):
    current_time = datetime.now()
    cache_key = f"{to_email}_{current_time.year}_{current_time.month}_{current_time.hour}"
    cache_key = hashlib.sha512(cache_key.encode('utf-8')).hexdigest()
    email_count = cache.get(cache_key, 0)

    max_email_count = 20
    if email_count >= max_email_count:
        return True

    email_count += 1
    cache.set(cache_key, email_count, 7200)
    return False
