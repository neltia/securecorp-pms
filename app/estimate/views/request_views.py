# django
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages
from estimate.utils import encrypt_urlsafe
# app
from django.forms import formset_factory
from estimate.forms import ProjectInfoForm, ProjectAdminForm
from estimate.forms import ProjectBaselineForm
from estimate.utils import manage_token
# db
from estimate.db_controller import db_domain, db_users
from estimate.db_controller import db_estimate
# email
from estimate.utils import send_mail


# 이메일 인증
# - 토큰 검사
# - 사용자 정보 업데이트
# - 영업 담당자에게 메일 발송
def verify_email(request, uidb64, token):
    # 토큰이 세션에 저장돼 있지 않은 경우
    session_token = request.session.get('email_verification_token')
    if not session_token:
        messages.error(request, '유효하지 않은 접근입니다.')
        return redirect("estimate:request_contact")

    # 토큰 생성시간 기준 확인
    expire_hour = 3
    if manage_token.is_expire_token(token, expire_hour):
        messages.error(request, '만료된 URL입니다.')
        return redirect("estimate:request_contact")

    # 세션과 토큰 상호 확인
    if token == session_token:
        is_email_verification = request.session['is_email_verification']
        customer_user = request.session['customer_user']

        # 이메일 신규 인증 확인
        if not is_email_verification:
            # 이메일 신규/재 인증 시 기존 세션 데이터 삭제
            if "estimate_info" in request.session:
                del request.session["estimate_info"]
            if "estimate_admin" in request.session:
                del request.session["estimate_admin"]

            # 영업 담당자들에게 이메일 발송
            group_name = "영업"
            sales_emails = db_users.get_emails_ingroup(group_name)
            for _username, email in sales_emails:
                send_mail.alert_email(email, customer_user)
            request.session['is_email_verification'] = True

        # - 프로젝트 정보 입력 함수 전달
        return redirect("estimate:project_inspection", uidb64=uidb64, token=token)
    else:
        messages.error(request, '유효하지 않은 토큰입니다.')
        return redirect("estimate:request_contact")


# 프로젝트 정보 입력 (1/2)
# - 토큰 검사
# - 사용자 정보를 확인해 is_active가 True인지 확인
# - 검사 결과 통과 시 정보 입력 페이지 반환
def project_inspection(request, uidb64, token):
    if "customer_user" not in request.session:
        messages.error(request, '유효하지 않은 접근입니다.')
        return redirect("estimate:request_contact")
    customer = request.session["customer_user"]

    # <GET>
    if request.method != "POST":
        request.session["estimate_req"] = False

        if "estimate_info" in request.session:
            project_info_form = ProjectInfoForm(initial=request.session["estimate_info"])
        else:
            project_info_form = ProjectInfoForm()
        if "estimate_admin" in request.session:
            project_admin_form = ProjectAdminForm(initial=request.session["estimate_admin"])
        else:
            project_admin_form = ProjectAdminForm()

        context = {
            "customer": customer,
            "project_info_form": project_info_form,
            "project_admin_form": project_admin_form
        }
        return render(request, "estimate/request/project_inspection.html", context=context)

    # <POST>
    project_info_form = ProjectInfoForm(request.POST)
    project_admin_form = ProjectAdminForm(request.POST)
    if not project_info_form.is_valid() or not project_admin_form.is_valid():
        messages.warning(request, "입력 데이터 확인 후 다시 제출해주세요.")
        return redirect("estimate:project_inspection", uidb64=uidb64, token=token)

    estimate_info = project_info_form.cleaned_data
    estimate_admin = project_admin_form.cleaned_data
    request.session["estimate_req"] = True
    request.session["estimate_info"] = estimate_info
    request.session["estimate_admin"] = estimate_admin

    return redirect("estimate:project_baseline", uidb64=uidb64, token=token)


# 프로젝트 정보 입력 (2/2)
# - 토큰 검사
# - 사용자 정보를 확인해 is_active가 True인지 확인
# - (1/2)에서 받은 정보를 바탕으로 공수 산정 정보 입력 페이지 반환
def project_baseline(request, uidb64, token):
    # formset
    email_addr = encrypt_urlsafe.decode(uidb64)
    project_info = request.session["estimate_info"]
    project_scope = project_info["project_scope"]
    baseline_formset = formset_factory(
        ProjectBaselineForm,
        extra=len(project_scope)
    )

    # <GET>
    if request.method != "POST":
        if not request.session["estimate_req"]:
            return redirect("estimate:project_inspection", uidb64=uidb64, token=token)

        project_admin = request.session["estimate_admin"]
        context = {
            "uidb64": uidb64,
            "token": token,
            "project_info": project_info,
            "project_admin": project_admin,
            "baseline_form": baseline_formset,
        }
        return render(request, "estimate/request/project_baseline.html", context=context)

    # <POST>
    formset = baseline_formset(request.POST, request.FILES, prefix='form')
    formset.is_bound = True
    if not formset.is_valid():
        messages.warning(request, "입력 데이터 확인 후 다시 제출해주세요.")
        return redirect("estimate:project_inspection", uidb64=uidb64, token=token)

    # 삽입 대상 데이터 전처리
    form_data_dict = dict()
    for form in formset:
        data = form.cleaned_data
        form_data_dict[form.prefix] = data

    # MD 공수 계산
    md_sum = 0
    md_process = dict()
    # - 신규 구축 프로젝트는 5MD 추가
    if project_info["project_type"] == "신규 구축":
        md_sum += 5
        md_process["신규 구축"] = 5
    # - 프로젝트 유형 별 초기 MD 증가치
    init_scope_md = settings.INIT_SCOPE_MD
    for scope, data in zip(project_scope, form_data_dict):
        form_data = form_data_dict[data]
        # validation
        if "calc_criteria" not in form_data:
            messages.warning(request, "입력 데이터 확인 후 다시 제출해주세요.")
            return redirect("estimate:project_inspection", uidb64=uidb64, token=token)

        # md calc
        calc_criteria = form_data["calc_criteria"]
        criteria_value = form_data[calc_criteria]
        md_value = init_scope_md[scope]
        if calc_criteria == "screen_num":
            md_value = round(criteria_value/settings.SCREEN_CRITERIA)
        elif calc_criteria == "url_num":
            md_value = round(criteria_value/settings.URL_CRITERIA)
        if md_value != 0:
            md_process[scope] = md_value
        md_sum += md_value

    mm_value = round(md_sum/20)
    request.session['md_process'] = md_process
    request.session['md_result'] = md_sum
    request.session['mm_result'] = mm_value
    request.session['is_md_calc'] = True

    # MD 공수 계산 결과 DB에 저장
    session_data = request.session
    claimant = request.session["customer_user"]
    doc_id = db_estimate.create_doc(session_data, email_addr)
    estimate_doc = db_estimate.find_doc(doc_id)

    # 첨부 파일 최대 크기 설정: 30MB
    max_size = 30
    max_file_size = 1024 * 1024 * max_size

    # Register new file
    for scope, data in zip(project_scope, form_data_dict):
        form_data = form_data_dict[data]
        file_obj = form_data["project_file"]
        if not file_obj:
            continue

        if file_obj.size > max_size:
            messages.warning(request, f"첨부 파일의 용량 제한은 {max_size}MB입니다.")
            return redirect("estimate:project_inspection", uidb64=uidb64, token=token)

        db_estimate.create_file(estimate_doc=estimate_doc, project_scope=scope, file_obj=file_obj)

    # MD 계산 결과를 영업 담당자에게 메일로 보내야 함
    domain = get_current_site(request).domain
    group_name = "영업"
    sales_emails = db_users.get_emails_ingroup(group_name)
    for username, email in sales_emails:
        send_mail.req_email(username, email, domain, claimant, doc_id)
    return redirect("estimate:request_chk", uidb64=uidb64, token=token)


# 공수산정 요청 완료 페이지 반환
def request_chk(request, uidb64, token):
    # 입력된 데이터 확인
    if "md_process" not in request.session:
        return redirect("estimate:project_inspection", uidb64=uidb64, token=token)

    # 요청 완료 시 이전에 저장된 세션 데이터는 모두 지움
    request.session.clear()

    # 요청 완료 메시지 전달
    context = {
        "success_title": "공수산정 요청 완료",
        "success_content": "영업 담당자에게 공수산정 요청이 발송되었습니다. 승인까지 잠시만 기다려주세요."
    }
    return render(request, "common/request_chk.html", context=context)
