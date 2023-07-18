# django
from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages
# app
from estimate.forms import ContactForm
# db
from estimate.db_controller import db_domain, db_users
# email
from estimate.utils import send_mail
from estimate.utils.manage_token import generate_token
from estimate.utils.manage_cache import email_limit_chk


# 견적 신청 정보 입력
def contact_information(request):
    # <GET>
    if request.method != "POST":
        contact_form = ContactForm()
        context = {"contact_form": contact_form}
        return render(request, "estimate/request/contact.html", context=context)

    # <POST>
    contact_form = ContactForm(request.POST)
    if not contact_form.is_valid():
        messages.warning(request, "입력 데이터 확인 후 다시 제출해주세요.")
        return redirect("estimate:request_contact")

    contact_data = contact_form.cleaned_data
    to_email = contact_data["email"]
    cc_myself = contact_data["cc_myself"]
    if not cc_myself:
        msg = "개인정보 수집 동의가 필요합니다."
        messages.warning(request, msg)
        return redirect("estimate:request_contact")

    # 도메인 점검
    is_domain_contains = db_domain.is_registered(to_email)
    if not is_domain_contains:
        messages.error(request, 'PMS에 등록되지 않은 도메인입니다.')
        return redirect("estimate:request_contact")

    # 메일 전송
    current_site = get_current_site(request)
    domain = current_site.domain
    token = generate_token(to_email)
    request.session['is_email_verification'] = False
    request.session['customer_user'] = contact_data
    request.session['email_verification_token'] = token

    # - 이메일 전송 횟수 제한: 시간 당 20회
    is_email_limit = email_limit_chk(to_email)
    if is_email_limit:
        messages.error(request, '과도한 신청 요청이 감지되었습니다. (시간당: 20건 제한)')
        return redirect("estimate:request_contact")

    # - 사용자 인증 요청 메일 발송
    res_code, result = send_mail.cert_email(to_email, domain, token)

    # 메일 반환 결과 확인
    if res_code == 200:
        msg = "이메일 인증 링크를 보냈습니다. 이메일을 확인해주세요."
        messages.success(request, msg)
    # 내부 AWS SES 발송 계정 키 인증 실패
    elif res_code == 500:
        msg = "이메일 주소로 메일 전송 중 예기치 못한 서버 오류가 발생했습니다."
        messages.warning(request, msg)
    else:
        msg = "이메일 주소로 메일 전송 중 예기치 못한 서버 오류가 발생했습니다."
        messages.warning(request, msg)
    return redirect("estimate:request_contact")
