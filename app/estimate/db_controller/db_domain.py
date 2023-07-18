from estimate.models import RegisteredDomain


# 도메인 등록 여부 조회
def is_registered(to_email):
    to_domain = to_email.split("@")[-1]
    try:
        RegisteredDomain.objects.get(email=to_domain)
        is_domain_contains = True
    except RegisteredDomain.DoesNotExist:
        is_domain_contains = False
    return is_domain_contains
