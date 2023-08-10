from django import forms
from django.contrib.auth.forms import PasswordChangeForm


# 아이디는 세션에서 받고, 영업 담당자의 비밀번호만 입력받는 폼
class SalesManagerLogin(forms.Form):
    password = forms.CharField(label='비밀번호', widget=forms.PasswordInput)


# 기존 장고 제공 비밀번호 변경 폼 한글화
class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 필드 라벨 변경
        self.fields['old_password'].label = '기존 비밀번호'
        self.fields['new_password1'].label = '새로운 비밀번호'
        self.fields['new_password2'].label = '새로운 비밀번호 확인'

        # 오류 메시지 변경
        self.fields['old_password'].error_messages = {
            'required': '기존 비밀번호를 입력해주세요.',
            'password_incorrect': '잘못된 기존 비밀번호입니다.',
        }

        self.fields['new_password1'].error_messages = {
            'required': '새로운 비밀번호를 입력해주세요.',
            'password_mismatch': '새로운 비밀번호와 확인 비밀번호가 일치하지 않습니다.',
            'password_too_short': '비밀번호는 최소 8자 이상이어야 합니다.',
            'password_common': '너무 흔한 비밀번호입니다.',
        }

        self.fields['new_password2'].error_messages = {
            'required': '확인 비밀번호를 입력해주세요.',
        }

        # 텍스트 변경
        self.fields['new_password1'].help_text = '비밀번호는 다음 사항을 만족해야 합니다.'
        self.fields['new_password1'].help_text += '<ul>'
        self.fields['new_password1'].help_text += '<li>다른 개인 정보와 유사하면 안 됩니다.</li>'
        self.fields['new_password1'].help_text += '<li>최소 8자 이상이어야 합니다.</li>'
        self.fields['new_password1'].help_text += '<li>널리 사용되지 않아야 합니다.</li>'
        self.fields['new_password1'].help_text += '<li>전부 숫자로 이루어질 수 없습니다.</li>'
        self.fields['new_password1'].help_text += '</ul>'
