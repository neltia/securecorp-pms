from django.conf import settings
import subprocess
import os
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


# cli command
def execute_command(command):
    if os.getenv("DJANGO_SETTINGS_MODULE") == "config.settings.debug":
        print('[+] command executed:', command)

    # shell: '/bin/bash'
    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
        executable="/bin/bash",
        timeout=30
    )
    returncode = result.returncode
    stdout = result.stdout.decode('utf-8').strip("\n")

    # error exception
    if returncode != 0 and returncode != 1:
        stdout = f"Error: ({returncode}):\n{stdout}"

    # return result
    return returncode, stdout


# excel file convert pdf file
def excel2pdf(report_name, excel_path):
    returncode = 0

    doc_path = os.path.join(settings.MEDIA_ROOT, 'result_estimate_doc')
    # 디렉터리 생성: 이미 있으면 무시
    os.makedirs(doc_path, exist_ok=True)

    pdf_name = urlsafe_base64_encode(force_bytes(report_name))
    pdf_path = f"{doc_path}/{pdf_name}.pdf"

    if os.path.exists(pdf_path):
        return returncode, pdf_path

    command = f"libreoffice --headless --convert-to pdf --outdir {doc_path} {excel_path}"
    returncode, stdout = execute_command(command)
    print(returncode, stdout)

    os.rename(f"{doc_path}/{report_name}.pdf", pdf_path)

    return 0, pdf_path
