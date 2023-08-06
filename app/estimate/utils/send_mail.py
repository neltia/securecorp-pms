from django.urls import reverse
# encoding
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
import base64
import hashlib
# boto3
from django.conf import settings
import boto3
from botocore.exceptions import NoCredentialsError
from botocore.exceptions import ClientError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication


# region_name = "us-east-1"
source_mail = "no-reply@securecorpapp.com"


# PMS->고객사: 신규 고객사 메일 인증 요청
def cert_email(to_email, domain, token):
    # 메일 제목
    subject = "[시큐어코퍼] PMS 견적관리 - 이메일 인증"

    # 기본 텍스트
    body_text = "안녕하세요. 시큐어큐퍼 PMS 서비스입니다.\n"
    body_text += "다음 링크를 클릭하여 공수산정을 위한 정보를 기입해주시면 견적서를 받을 수 있습니다.\n"
    body_text += "링크는 1시간 뒤에 만료됩니다.\n"
    # - 인증 링크 추가
    uid = urlsafe_base64_encode(force_bytes(to_email))
    url = reverse("estimate:verify_email", kwargs={"uidb64": uid, "token": token})
    ret_link = f'http://{domain}{url}'
    body_text += ret_link

    # 메일 송신 요청
    res_code, result = ses_mail_send(to_email, subject, body_text)
    return res_code, result


# [이메일 인증 완료] PMS->영업 담당자: 담당자들에게 신규 인증 알림 메일
def alert_email(to_email, verified_customer):
    # var declare
    company_name = verified_customer["company_name"]
    user_name = verified_customer["user_name"]

    # 메일 제목
    subject = "[시큐어코퍼] PMS 견적관리 - 고객사 신규 견적 요청 알림"

    # 기본 텍스트
    body_text = "안녕하세요. 시큐어큐퍼 PMS 서비스입니다.\n"
    body_text += f"{company_name} 회사의 {user_name}님이 이메일 인증을 완료헸습니다.\n"

    # 메일 송신 요청
    res_code, result = ses_mail_send(to_email, subject, body_text)
    return res_code, result


# [공수산정 요청 완료] PMS->영업 담당자: 담당자들에게 요청된 공수산정 정보 링크 발송
def req_email(username, to_email, domain, claimant, doc_id):
    # var declare
    company_name = claimant["company_name"]
    user_name = claimant["user_name"]

    # 메일 제목
    subject = "[시큐어코퍼] PMS 견적관리 - 고객사 견적 신청 공수 요청 알림"

    # 메일 내용
    # - 기본 텍스트
    body_text = "안녕하세요. 시큐어큐퍼 PMS 서비스입니다.\n"
    body_text += f"{company_name} 회사의 {user_name}님으로부터 공수산정 요청이 발송되었습니다.\n"
    # - 결과 페이지 링크 추가
    username = urlsafe_base64_encode(force_bytes(username))
    url = reverse("estimate:response_chk", kwargs={"doc_id": doc_id, "sales_manager_id": username})
    ret_link = f'http://{domain}{url}'
    body_text += ret_link

    # 메일 송신 요청
    res_code, result = ses_mail_send(to_email, subject, body_text)
    return res_code, result


# [공수산정 결과 발송] PMS->견적 요청자: 영업 담당자가 승인한 공수산정 결과를 엑셀->PDF 변환 과정을 거쳐 PDF 견적 요청서 발송
def res_email(to_email, domain, file_path, filename):
    # 메일 제목
    subject = "[시큐어코퍼] PMS 견적관리 - 공수산정 견적서 발송"

    # 메일 내용
    body_text = "안녕하세요. 시큐어큐퍼 PMS 서비스입니다.\n"
    body_text += "요청주셨던 공수산정 견적 신청 결과 파일을 송부합니다.\n"

    # 메일 송신 요청
    res_code, result = mail_send_withfile(to_email, subject, body_text, file_path, filename)
    return res_code, result


# boto client setting
def boto_client_cert(service_name, region_name="ap-northeast-2"):
    # client = boto3.client(service_name)
    client = boto3.client(
        service_name,
        region_name=region_name,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )
    return client


# aws ses with boto3
def ses_mail_send(to_email, subject, body_text):
    ses_client = boto_client_cert("ses")
    try:
        response = ses_client.send_email(
            Source = source_mail,
            Destination = {'ToAddresses': [to_email]},
            Message = {
                "Subject": {
                    "Charset": "UTF-8",
                    "Data": subject
                },
                "Body": {
                    "Text": {
                        "Charset": "UTF-8",
                        "Data": body_text
                    }
                }
            }
        )
    except NoCredentialsError:
        res_code = 500
        result = "AWS SES 발송 계정 정보를 찾을 수 없음"
        return res_code, result
    except ClientError as e:
        result = e
        if "Email address is not verified" in str(e):
            res_code = 401
            return res_code, result
        res_code = -1
        return res_code, result
    else:
        res_code = response["ResponseMetadata"]["HTTPStatusCode"]
        result = response["MessageId"]
    return res_code, result


# aws ses with boto3, file attachement
def mail_send_withfile(to_email, subject, body_text, file_path, filename):
    ses_client = boto_client_cert("ses")

    msg = MIMEMultipart()
    msg["From"] = source_mail
    msg["Subject"] = subject

    # set message body
    body = MIMEText(body_text, "plain")
    msg.attach(body)

    # set file
    # - file_path_chk
    if isinstance(file_path, str):
        file_path_list = [file_path]
    # add header
    for path in file_path_list:
        with open(path, "rb") as attachment:
            part = MIMEApplication(attachment.read())
            part.add_header(
                "Content-Disposition",
                "attachment",
                filename=f"{filename}.pdf"
            )
    msg.attach(part)

    try:
        response = ses_client.send_raw_email(
            Source=source_mail,
            Destinations=[to_email],
            RawMessage={"Data": msg.as_string()}
        )
    except NoCredentialsError:
        res_code = 500
        result = "AWS SES 발송 계정 정보를 찾을 수 없음"
        return res_code, result
    except ClientError as e:
        result = e
        if "Email address is not verified" in str(e):
            res_code = 401
            return res_code, result
        res_code = -1
        return res_code, result
    else:
        res_code = response["ResponseMetadata"]["HTTPStatusCode"]
        result = response["MessageId"]
    return res_code, result
