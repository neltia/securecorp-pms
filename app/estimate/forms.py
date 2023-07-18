from django import forms
from django.core.validators import RegexValidator


class ContactForm(forms.Form):
    user_name = forms.CharField(label="이름", max_length=20)
    tell_regex = RegexValidator(regex=r"^\+?1?\d{8,15}$")
    phone_number = forms.CharField(
        label="연락처",
        validators=[tell_regex], max_length=16
    )
    company_name = forms.CharField(label="회사명", max_length=100)
    email = forms.EmailField(label="이메일")
    cc_myself = forms.BooleanField(label="개인정보 수집 동의", required=False)


class LabelOnlyWidget(forms.Widget):
    def __init__(self, label=None, attrs=None):
        super().__init__(attrs)
        self.label = label

    def render(self, name, value, attrs=None, renderer=None):
        if self.label:
            return self.label
        return ''


class ProjectInfoForm(forms.Form):
    project_type_opt = (
        ('신규 구축', '신규 구축'),
        ('수정 개발', '수정 개발'),
    )
    project_scope_opt = (
        ('PC WEB', 'PC WEB'),
        ('Mobile WEB', 'Mobile WEB'),
        ('Android APP', 'Android APP'),
        ('iOS APP', 'iOS APP'),
        ('관리자 WEB', '관리자 WEB'),
        ('CS Program', 'CS Program'),
    )
    label_text = "※ 한 개의 서비스 기준으로 입력하시기 바랍니다. 다수의 서비스가 한 프로젝트인 경우 각각 입력하십시오."

    project_name = forms.CharField(label="프로젝트명", max_length=100)
    project_type = forms.ChoiceField(
        label="프로젝트 분류",
        choices=project_type_opt,
        widget=forms.RadioSelect
    )
    project_scope = forms.MultipleChoiceField(
        label="프로젝트 범위",
        choices=project_scope_opt,
        widget=forms.CheckboxSelectMultiple
    )
    label = forms.CharField(
        label=label_text,
        required=False, widget=LabelOnlyWidget
    )
    project_description = forms.CharField(
        label="프로젝트 설명",
        widget=forms.TextInput(attrs={'placeholder': '예시) 쇼핑몰 시스템 구축을 위한 신규 프로젝트'})
    )


class ProjectAdminForm(forms.Form):
    tell_regex = RegexValidator(regex=r"^\+?1?\d{8,15}$")

    project_admin_company = forms.CharField(label="회사명", max_length=100)
    project_admin_name = forms.CharField(label="이름", max_length=20)
    project_admin_phone = forms.CharField(
        label="연락처",
        validators=[tell_regex], max_length=16
    )
    project_admin_email = forms.EmailField(label="이메일")


class ProjectBaselineForm(forms.Form):
    criteria_opt = (
        ('screen_num', '화면 수'),
        ('url_num', 'URL 수'),
    )

    calc_criteria = forms.ChoiceField(
        label="공수산정 기초 입력기준",
        choices=criteria_opt,
        widget=forms.RadioSelect(attrs={'onchange': 'handleSelectChange(this)'})
    )

    screen_num = forms.IntegerField(
        label="",
        required=False,
        widget=forms.NumberInput(attrs={'style': 'display: none', 'placeholder': "화면 수 (단위: 개)"})
    )
    url_num = forms.IntegerField(
        label="",
        required=False,
        widget=forms.NumberInput(attrs={'style': 'display: none', 'placeholder': "URL 수 (단위: 개)"})
    )
    project_file = forms.FileField(label="프로젝트 자료 업로드", required=False)


class mdEditableForm(forms.Form):
    md_value = forms.IntegerField(label="투입 공수")
