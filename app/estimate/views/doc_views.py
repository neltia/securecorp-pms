# django
from django.shortcuts import render, redirect
from django.contrib import messages
from estimate.utils import encrypt_urlsafe
# app
from estimate.decorators.verfication import manager_required
from django.forms import formset_factory
from estimate.forms import ProjectInfoForm, ProjectAdminForm
from estimate.forms import ProjectBaselineForm
# db
from django.forms.models import model_to_dict
from estimate.db_controller import db_estimate
# file process
from django.conf import settings
from django.http import FileResponse
import os, json


# 파일 지정 뷰어
def download_file(request, file_path, file_type):
    if file_type == "upload":
        file_full_path = os.path.join(settings.MEDIA_ROOT, f"upload_files/{file_path}")
    elif file_type == "report":
        file_full_path = os.path.join(settings.MEDIA_ROOT, f"result_estimate_doc/{file_path}")

    file_name = os.path.basename(file_full_path)
    response = FileResponse(open(file_full_path, 'rb'))
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(file_name)
    return response


# 견적서 데이터 목록 페이지
@manager_required
def doc_list(request):
    user_id = encrypt_urlsafe.encode(request.user)

    # doc sorting
    sort = request.GET.get('sort','')
    sort_target = [
        "md_result", "project_type", "project_admin",
        "apply_date", "update_date", "approved_date"
    ]
    if sort in sort_target:
        doc_list = db_estimate.all_doc().order_by(f'-{sort}','-id')
    else:
        doc_list = db_estimate.all_doc().order_by('-id')

    # return doc list
    doc_dict_list = list()
    for doc in doc_list:
        data = model_to_dict(doc)
        data["doc_id"] = doc.doc_id
        doc_dict_list.append(data)
    context = {"user_id": user_id, "estimate_list": doc_dict_list}
    return render(request, "estimate/doc/list.html", context=context)


# 단일 견적 문서 확인 페이지
@manager_required
def doc_view(request, doc_id):
    # data init
    estimate_doc = db_estimate.find_doc(doc_id)
    doc_files = db_estimate.get_doc_files(estimate_doc)

    estimate_doc = model_to_dict(estimate_doc)
    claimant = json.loads(estimate_doc["claimant"])

    context = {
        "doc_id": doc_id, "claimant": claimant,
        "estimate_doc": estimate_doc, "doc_files": doc_files,
    }
    return render(request, "estimate/doc/view.html", context=context)


# 단일 견적 문서 수정 페이지 (1/2)
@manager_required
def doc_edit(request, doc_id):
    # <GET>
    if request.method != "POST":
        # form init
        project_info_form = ProjectInfoForm
        project_admin_form = ProjectAdminForm

        # data init
        estimate_doc = db_estimate.find_doc(doc_id)
        estimate_doc = model_to_dict(estimate_doc)
        claimant = json.loads(estimate_doc["claimant"])
        project_admin = json.loads(estimate_doc["project_admin"])

        if "estimate_info" in request.session:
            info_initial = request.session["estimate_info"]
        else:
            info_initial = {
                "project_name": estimate_doc["project_name"],
                "project_type": estimate_doc["project_type"],
                "project_scope": json.loads(estimate_doc["project_scope"]),
                "project_description": estimate_doc["project_description"]
            }
        if "estimate_admin" in request.session:
            admin_initial = request.session["estimate_admin"]
        else:
            admin_initial = project_admin

        # return data
        context = {
            "doc_id": doc_id, "claimant": claimant,
            "estimate_doc": estimate_doc,
            "project_info_form": project_info_form(initial=info_initial),
            "project_admin_form": project_admin_form(initial=admin_initial),
        }
        return render(request, "estimate/doc/edit.html", context=context)

    # <POST>
    # 폼 유효성 검사
    project_info_form = ProjectInfoForm(request.POST)
    project_admin_form = ProjectAdminForm(request.POST)
    if not project_info_form.is_valid() or not project_admin_form.is_valid():
        messages.warning(request, "입력 데이터 확인 후 다시 제출해주세요.")
        return redirect("estimate:doc_edit", doc_id=doc_id)

    # 데이터 갱신
    estimate_info = project_info_form.cleaned_data
    estimate_admin = project_admin_form.cleaned_data
    request.session["estimate_info"] = estimate_info
    request.session["estimate_admin"] = estimate_admin

    return redirect("estimate:doc_edit_md", doc_id=doc_id)


# 단일 견적 문서 수정 페이지 (2/2)
def doc_edit_md(request, doc_id):
    # formset
    if "estimate_info" not in request.session:
        messages.warning(request, "프로젝트 정보가 입력되지 않았습니다.")
        return redirect("estimate:doc_edit", doc_id=doc_id)
    project_info = request.session["estimate_info"]
    project_admin = request.session["estimate_admin"]
    project_scope = project_info["project_scope"]
    baseline_formset = formset_factory(
        ProjectBaselineForm,
        extra=len(project_scope)
    )

    # <GET>
    if request.method != "POST":
        # form init
        project_info_form = ProjectInfoForm
        project_admin_form = ProjectAdminForm

        # data init
        estimate_doc = db_estimate.find_doc(doc_id)
        doc_files = db_estimate.get_doc_files(estimate_doc)
        estimate_doc = model_to_dict(estimate_doc)

        # return data
        context = {
            "doc_id": doc_id, "doc_files": doc_files,
            "estimate_doc": estimate_doc,
            "project_info": project_info, "baseline_form": baseline_formset,
        }
        return render(request, "estimate/doc/edit_md.html", context=context)

    # <POST>
    # 폼 유효성 검사
    formset = baseline_formset(request.POST, request.FILES, prefix='form')
    formset.is_bound = True
    if not formset.is_valid():
        messages.warning(request, "입력 데이터 확인 후 다시 제출해주세요.")
        return redirect("estimate:doc_edit_md", doc_id=doc_id)

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
            return redirect("estimate:doc_edit_md", doc_id=doc_id)

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

    # 데이터 갱신
    about_data = {
        "project_admin": json.dumps(project_admin, ensure_ascii=False),
        "project_name": project_info["project_name"],
        "project_type": project_info["project_type"],
        "project_scope": json.dumps(project_scope, ensure_ascii=False),
        "project_description": project_info["project_description"],
        "md_process": json.dumps(md_process, ensure_ascii=False),
        "md_result": md_sum,
        "mm_result": mm_value
    }
    db_estimate.update_doc(doc_id, "all", about_data)

    messages.success(request, "수정되었습니다.")
    return redirect("estimate:doc_view", doc_id=doc_id)


# 견적 승인 취소
@manager_required
def doc_revoke_approve(request, doc_id):
    estimate_doc = db_estimate.find_doc(doc_id)
    estimate_doc.is_approved = False
    estimate_doc.save()

    messages.success(request, "승인이 취소되었습니다.")
    return redirect('estimate:doc_view', doc_id=doc_id)


# 단일 견적서 데이터 삭제
@manager_required
def doc_del(request, doc_id):
    db_estimate.delete_doc(doc_id)
    return redirect('estimate:doc_list')
