# django
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
# app
from estimate.decorators.verfication import manager_required
from managers.forms import SalesManagerLogin
# db
from estimate.db_controller import db_users
from estimate.db_controller import db_estimate


def manager_login(request):
    username = ""
    if "sales_manager_id" in request.session:
        username = request.session["sales_manager_id"]

    # <GET>
    if request.method != "POST":
        next_url = request.GET.get('next', '/')
        login_form = SalesManagerLogin
        context = {"user_name": username, "next_url": next_url, "login_form": login_form}
        return render(request, "managers/login.html", context)

    # <POST>
    next_url = request.GET.get('next', '/')
    if username == "":
        username = request.POST.get("salesManagerId")
    password = request.POST.get("password")
    user = authenticate(request, username=username, password=password)
    if user is None:
        msg = "입력된 계정 정보가 올바르지 않습니다."
        messages.warning(request, msg)
        authentication_form_url = f'/managers/login/?next={next_url}'
        return redirect(authentication_form_url)

    login(request, user)
    return redirect(next_url)


@manager_required
def manager_logout(request):
    request.session.clear()
    return redirect("pms_index")


@manager_required
def manger_profile(request):
    user_in_group = db_users.get_user_groups(request.user)
    approved_doc_list = db_estimate.find_by_approved(request.user)

    context = {"groups": user_in_group, "estimate_list": approved_doc_list}
    return render(request, "managers/profile.html", context)
