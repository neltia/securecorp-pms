from django.utils.encoding import force_str, force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.http import Http404
from django.utils.encoding import DjangoUnicodeDecodeError


def encode(string):
    try:
        string = urlsafe_base64_encode(force_bytes(string))
    except ValueError:
        raise Http404
    return string


def decode(string):
    try:
        string = force_str(urlsafe_base64_decode(string))
    except (ValueError, DjangoUnicodeDecodeError):
        raise Http404
    return string
