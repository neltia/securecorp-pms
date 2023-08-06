# django
from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages
from estimate.utils import encrypt_urlsafe
# app
from estimate.decorators.verfication import manager_required
from estimate.forms import MdEditableForm
# db
from django.forms.models import model_to_dict
from estimate.db_controller import db_estimate
from django.core.exceptions import ValidationError
import os, json
# email
from estimate.utils import send_mail
# excel reporting
from django.conf import settings
from estimate.utils.gen_excel import create_report
from estimate.utils.convert_pdf import excel2pdf
from pdf2image import convert_from_path


# 공수산정 결과 페이지
def response_chk(request, doc_id, sales_manager_id):
    # email param chk
    user_id = encrypt_urlsafe.decode(sales_manager_id)

    # is user auth
    request.session["sales_manager_id"] = user_id
    if not request.user.is_authenticated:
        next_url = request.get_full_path()
        authentication_form_url = f'/managers/login/?next={next_url}'
        return redirect(authentication_form_url)

    # <GET>: return estimate doc
    if request.method != "POST":
        estimate_doc = db_estimate.find_doc(doc_id)
        estimate_doc_dict = model_to_dict(estimate_doc)
        doc_files = db_estimate.get_doc_files(estimate_doc)

        if estimate_doc_dict["is_approved"]:
            approved_user = estimate_doc_dict["approved_user"]
            msg = f"{approved_user}님이 승인한 문서입니다."
            messages.warning(request, msg)
            return redirect("estimate:doc_list")

        context = {
            "sales_manager_id": user_id, "doc_id": doc_id,
            "estimate_doc": estimate_doc_dict, "doc_files": doc_files,
            "md_form": MdEditableForm
        }
        return render(request, "estimate/response/chk_doc.html", context=context)

    # <POST>: mm value update and redirect estimate send page
    md_editable_form = MdEditableForm(request.POST)
    if md_editable_form.is_valid():
        md_editable_data = md_editable_form.cleaned_data
        db_estimate.update_doc(doc_id, "md_value", md_editable_data)

    return redirect("estimate:report_chk", doc_id)


# 견적서 확인 및 발송 페이지
@manager_required
def report_chk(request, doc_id):
    # data init
    estimate_doc = db_estimate.find_doc(doc_id)
    estimate_doc_dict = model_to_dict(estimate_doc)
    claimant = json.loads(estimate_doc_dict["claimant"])
    user_id = encrypt_urlsafe.encode(request.user)

    # 첫 승인이면 새 발행 번호 부여하고 아니면 외래키를 사용해 발행 값 탐색
    try:
        estimate_num = db_estimate.publish_num(estimate_doc)
    except ValidationError:
        estimate_num = db_estimate.find_pubnum(estimate_doc)

    # 승인 상태로 변경
    about_data = {"approved_user": request.user.username}
    db_estimate.update_doc(doc_id, "approve", about_data)

    # 엑셀 파일 생성
    returncode, report_name, excel_path = create_report(claimant, estimate_doc_dict, estimate_num)

    # Excel2PDF 파일 변환
    returncode, pdf_path = excel2pdf(report_name, excel_path)

    # PDF 파일 뷰어
    media_url = settings.MEDIA_URL
    img_path = os.path.join(settings.MEDIA_ROOT, 'img_estimate_pdf')
    path = os.path.basename(pdf_path)
    img_name = f"{path.split('/')[-1][:-4]}.jpg"
    os.makedirs(img_path, exist_ok=True)

    pdf_image_path = f"{img_path}/{img_name}"
    pdf_image = convert_from_path(pdf_path)[0]
    pdf_image.save(pdf_image_path, "JPEG")

    request.session["report_path"] = pdf_path
    request.session["report_name"] = report_name

    context = {
        "claimant": claimant, "sales_manager_id": user_id,
        "doc_id": doc_id, "media_url": media_url,
        "pdf_image_path": img_name, "report_path": pdf_path.split('/')[-1]
    }
    return render(request, "estimate/response/chk_report.html", context=context)


# 견적서 발송 함수
@manager_required
def report_send(request, doc_id):
    # 견적서 내용 확인
    if "report_name" not in request.session:
        messages.warning(request, "잘못된 접근이거나 이미 발송된 견적서입니다.")
        return redirect("estimate:doc_list")

    # data init
    report_path = request.session["report_path"]
    report_name = request.session["report_name"]
    del request.session["report_path"]
    del request.session["report_name"]

    # doc select
    estimate_doc = db_estimate.find_doc(doc_id)
    estimate_doc = model_to_dict(estimate_doc)
    claimant = json.loads(estimate_doc["claimant"])
    user_id = encrypt_urlsafe.encode(request.user)
    claimant_email = claimant["email"]

    # mail send
    domain = get_current_site(request).domain
    send_mail.res_email(claimant_email, domain, report_path, report_name)

    # 요청 완료 메시지 전달
    context = {
        "success_title": "견적서 발송 완료",
        "success_content": "요청한 이메일로 견적서 파일을 발송했습니다."
    }
    return render(request, "common/request_chk.html", context=context)
