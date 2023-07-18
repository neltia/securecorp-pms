from django import forms


class SalesManagerLogin(forms.Form):
    password = forms.CharField(label='비밀번호', widget=forms.PasswordInput)
