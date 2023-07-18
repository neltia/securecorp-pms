from django.shortcuts import redirect, render
from django.contrib import messages
from estimate.utils import manage_token
from estimate.db_controller import db_users


# 이메일 인증을 거친 사용자만 정보 견적을 요청할 수 있음
def email_required(view_func):
    def wrapper(request, uidb64, token, *args, **kwargs):
        if 'email_verification_token' not in request.session:
            # 토큰이 세션에 없는 경우 이메일 인증을 받지 않은 것으로 간주
            messages.error(request, '유효하지 않은 접근입니다.')
            return redirect('estimate:request_contact')

        session_token = request.session['email_verification_token']

        # 토큰 생성시간 확인 등 추가 검증 로직
        expire_hour = 3
        token_created_at = token.split("-")[0]
        if manage_token.is_expire_token(token, expire_hour):
            messages.error(request, '만료된 URL입니다.')
            return redirect('estimate:request_contact')

        # 세션과 토큰 상호 확인
        if token != session_token:
            messages.error(request, '유효하지 않은 토큰입니다.')
            return redirect('estimate:request_contact')

        # 토큰 검증 및 이메일 활성화 여부 확인 로직
        if not request.session['is_email_verification']:
            messages.warning(request, '인증되지 않은 사용자입니다.')
            return redirect('estimate:request_contact')

        # 이메일 인증을 받은 경우 뷰 함수 실행
        return view_func(request, uidb64, token, *args, **kwargs)
    return wrapper


# 내부 담당자 로그인이 필요한 페이지는 담당자 로그인이 필요함
def manager_required(view_func):
    def wrapper(request, *args, **kwargs):
        # 인증: 세션에서 내부 담당자 로그인 여부 확인
        if not request.user.is_authenticated:
            next_url = request.get_full_path()
            authentication_form_url = f'/managers/login/?next={next_url}'
            return redirect(authentication_form_url)

        # 인가: 영업 그룹에 속한 사용자인지 확인
        is_member = db_users.is_member("영업", request.user)
        if not is_member:
            return render(request, '403.html', status=403)

        # 영업 그룹에 속한 사용자면 본래 뷰 함수 실행
        return view_func(request, *args, **kwargs)

    return wrapper
