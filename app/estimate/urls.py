from django.urls import path
from estimate import views
from . import views
from estimate.decorators.verfication import email_required


app_name = "estimate"

urlpatterns = [
    # 견적 요청
    path('request', views.contact_information, name="request_contact"),
    path('verify/<uidb64>/<token>/', views.verify_email, name='verify_email'),
    path('project/<uidb64>/<token>/',
        email_required(views.project_inspection),
        name='project_inspection'
    ),
    path('baseline/<uidb64>/<token>/',
        email_required(views.project_baseline),
        name='project_baseline'
    ),
    path('check/<uidb64>/<token>/',
        email_required(views.request_chk),
        name='request_chk'
    ),

    # 요청 견적 내용 확인 및 견적서 발송
    path('result/<doc_id>/<sales_manager_id>/',
        views.response_chk, name='response_chk'
    ),
    path('chk/<doc_id>/',
        views.report_chk, name='report_chk'
    ),
    path('send/<doc_id>/',
        views.report_send, name='report_send'
    ),

    # 요청 견적 목록 확인 및 관리
    path('doc/list/',
        views.doc_list, name='doc_list'
    ),
    path('doc/view/<doc_id>/',
        views.doc_view, name='doc_view'
    ),
    path('doc/edit/<doc_id>/',
        views.doc_edit, name='doc_edit'
    ),
    path('doc/edit/<doc_id>/md',
        views.doc_edit_md, name='doc_edit_md'
    ),
    path('doc/revoke/<doc_id>',
        views.doc_revoke_approve, name='doc_revoke'
    ),
    path('doc/delete/<doc_id>/',
        views.doc_del, name='doc_del'
    ),

    path('download/<str:file_path>/<str:file_type>',
        views.download_file, name='download_file'
    ),
]
