# - 장고 모델
from estimate.models import EstimateDoc
from estimate.models import EstimateFile
from estimate.models import EstimatePubNum
from django.shortcuts import get_object_or_404
# - data process
from django.utils import timezone
import hashlib
import json


# 새 견적 정보 삽입
def create_doc(session_data, email_addr):
    # data init
    claimant = session_data['customer_user']
    project_info = session_data["estimate_info"]
    project_scope = project_info["project_scope"]
    project_admin = session_data["estimate_admin"]
    md_process = session_data["md_process"]
    md_result = session_data["md_result"]
    mm_result = session_data["mm_result"]
    if "project_description" not in project_info:
        project_description = ""
    else:
        project_description = project_info["project_description"]

    # doc_id
    current_date = timezone.now()
    doc_id = hashlib.sha256(f"{email_addr}{current_date}".encode('utf-8')).hexdigest()
    estimate_doc = EstimateDoc.objects.create(
        doc_id=doc_id,
        claimant=json.dumps(claimant, ensure_ascii=False),
        project_admin=json.dumps(project_admin, ensure_ascii=False),
        project_name=project_info["project_name"],
        project_type=project_info["project_type"],
        project_scope=json.dumps(project_scope, ensure_ascii=False),
        project_description=project_description,
        md_process=json.dumps(md_process, ensure_ascii=False),
        md_result=md_result,
        mm_result=mm_result,
        apply_date=current_date,
        update_date=current_date,
        approved_date=None,
        is_approved=False,
        approved_user=None
    )
    return doc_id


# doc_id로 견적 정보 찾기
def find_doc(doc_id):
    estimate_doc = get_object_or_404(EstimateDoc, doc_id=doc_id)
    return estimate_doc


# 전체 견적 정보 찾기
def all_doc():
    estimate_doc_list = EstimateDoc.objects.all()
    return estimate_doc_list


# 특정 사용자가 승인한 견적 목록 찾기
def find_by_approved(approved_user):
    estimate_doc_list = EstimateDoc.objects.filter(approved_user=approved_user)
    return estimate_doc_list


# update doc
def update_doc(doc_id, data_type:str = None, about_data:dict = None):
    estimate_doc = find_doc(doc_id)

    # md_value 값만 수정하는 경우
    if data_type == "md_value":
        estimate_doc.md_result = about_data["md_value"]
        estimate_doc.mm_result = round(about_data["md_value"]/20)

    # 승인 상태만 업데이트하는 경우
    if data_type == "approve":
        if not estimate_doc.is_approved:
            estimate_doc.is_approved = True
        approved_user = about_data["approved_user"]
        estimate_doc.approved_user = approved_user
        estimate_doc.approved_date = timezone.now()

    # 전체 데이터를 업데이트하는 경우
    if data_type == "all":
        estimate_doc.project_admin = about_data["project_admin"]
        estimate_doc.project_name = about_data["project_name"]
        estimate_doc.project_type = about_data["project_type"]
        estimate_doc.project_scope = about_data["project_scope"]
        estimate_doc.project_description = about_data["project_description"]
        estimate_doc.md_process = about_data["md_process"]
        estimate_doc.md_result = about_data["md_result"]
        estimate_doc.mm_result = about_data["mm_result"]

    # update 수행 시 정보 갱신일 업데이트
    estimate_doc.update_date = timezone.now()
    estimate_doc.save()
    return estimate_doc


# delete doc
def delete_doc(doc_id):
    estimate_doc = find_doc(doc_id)
    estimate_doc.delete()
    return estimate_doc


# new project file
def create_file(estimate_doc, project_scope, file_obj):
    estimate_file = EstimateFile.objects.create(
        estimate_doc=estimate_doc,
        project_scope=project_scope,
        project_file=file_obj
    )


# get project files with doc_id
def get_doc_files(estimate_doc):
    doc_files = EstimateFile.objects.filter(estimate_doc=estimate_doc)
    return doc_files


# new publish DOC pdf num
def publish_num(estimate_doc):
    pub_num = EstimatePubNum(estimate_doc=estimate_doc)
    pub_num.save()

    doc_pub_num = pub_num.doc_pub_num
    return doc_pub_num


def find_pubnum(estimate_doc):
    obj = EstimatePubNum.objects.get(estimate_doc=estimate_doc)
    return obj.doc_pub_num
