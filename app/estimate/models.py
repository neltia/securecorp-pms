from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError


# 이메일을 전송 가능 도메인
class RegisteredDomain(models.Model):
    def __str__(self):
        return self.email

    email = models.CharField(
        max_length=128, unique=True,
        verbose_name="허용 도메인"
    )


# 견적 신청 정보 저장
class EstimateDoc(models.Model):
    def __str__(self):
        return f"견적 신청 정보 ID: {self.doc_id}"


    # 신청 정보 문서 식별 아이디
    doc_id = models.TextField(
        verbose_name="문서 아이디",
        unique=True, db_index=True, editable=False
    )

    # 견적 신청자 정보 (type: json)
    # - 이름, 회사, 전화번호, 이메일 정보 포함
    claimant = models.TextField(verbose_name="견적 신청자 정보")
    # 프로젝트 관리자 정보 (type: json)
    # * 견적 신청자와 기본 정보는 같게 설정되나 다를 수 있음
    project_admin = models.TextField(verbose_name="프로젝트 관리자 정보")

    # 프로젝트 정보
    # - 프로젝트명
    project_name = models.CharField(verbose_name="프로젝트 이름", max_length=50)
    # - 프로젝트 분류
    project_type = models.CharField(verbose_name="프로젝트 분류", max_length=10)
    # - 프로젝트 범위 (type: list)
    project_scope = models.TextField(verbose_name="프로젝트 범위")
    # - 프로젝트 설명
    project_description = models.CharField(verbose_name="프로젝트 설명", max_length=300)

    # MD 계산 정보 (type: json)
    md_process = models.TextField(verbose_name="공수계산 정보")
    md_result = models.IntegerField(verbose_name="공수계산 결과", default=0)
    mm_result = models.IntegerField(verbose_name="M/M", default=0)

    # 승인한 내부 영업 담당자
    approved_user = models.CharField(
        verbose_name="승인 담당자",
        max_length=20, blank=True, null=True
    )
    # 견적신청 일시, 정보 갱신 일시, 승인 일시
    apply_date = models.DateField(verbose_name="견적신청 일시", blank=True)
    approved_date = models.DateField(verbose_name="견적 승인 일시", blank=True, null=True)
    update_date = models.DateField(verbose_name="정보 갱신 일시", blank=True)

    # 이 공수산정 요청에 대한 승인 여부
    is_approved = models.BooleanField(
        verbose_name="요청 승인 여부",
        blank=True, null=True
    )


# 견적 신청 문서에 입력받는 문서당 1개 이상 파일들
# 1:N 관계
class EstimateFile(models.Model):
    def __str__(self):
        return f"프로젝트: {self.estimate_doc.project_name}, Path: {self.project_file.name}"

    estimate_doc = models.ForeignKey(EstimateDoc, blank=False, null=False, on_delete=models.CASCADE)
    project_scope = models.CharField(max_length=15)
    project_file = models.FileField(upload_to='upload_files/')


# 견적번호 할당
class EstimatePubNum(models.Model):
    def __str__(self):
        return self.doc_pub_num


    def save(self, *args, **kwargs):
        # 발행 상태 확인:
        # 첫 승인 전 번호를 발행하고, 승인으로 바꾸면 첫 승인 시에만 판단
        if not self.estimate_doc.is_approved:
            # 발행 번호 생성
            if not self.doc_pub_num:
                current_year = timezone.now().year
                current_year = str(current_year)[-2:]

                try:
                    last_published = EstimatePubNum.objects.latest("id")
                    last_number = int(last_published.doc_pub_num[3:])
                except EstimatePubNum.DoesNotExist:
                    last_number = -1

                current_number = last_number + 1
                new_number = f"A{current_year}{str(current_number).zfill(3)}"
                self.doc_pub_num = new_number
            super(EstimatePubNum, self).save(*args, **kwargs)  # 발행 번호 생성 후 저장
        else:
            raise ValidationError("이미 견적번호를 발행받은 견적 문서입니다.")


    doc_pub_num = models.CharField(max_length=7)
    estimate_doc = models.ForeignKey(EstimateDoc, blank=False, null=True, on_delete=models.SET_NULL)
