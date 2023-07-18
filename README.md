# Securecorp-PMS
시큐어코퍼 사 소속으로 개발한 프로젝트 관리 시스템
<br>
3단계 구성으로 회사 운영 업무를 자동화하고 적절한 공수를 산정하기 위함
- 1단계: 견적관리 -> 2단계: 프로젝트 진행관리 -> 3단계: 산출물 관리


## 프로젝트 소개
시큐어코퍼 사 소속으로 1인 개발한 프로젝트 관리 시스템 중 1단계, 견적관리에서 비즈니스 로직을 제거한 공개용 저장소입니다.<br>
특별한 비즈니스 로직이 없으니 Git에 공개해도 된다는 허락을 맡았습니다.

### 개발 기간
* 23.04.20 ~ 장고 프레임워크 학습 및 정리
* 23.05.08 ~ AWS SES 활용 이메일 기능 구현
* 23.05.22 ~ 메인 WAS 기능 개발 & 페이지 디자인 시작

### 개발 환경
- **Dev**       : AWS EC2, Docker Container & Vscode attach
- **Deploy**    : AWS Route53, AWS ELB, AWS ACM, docker-compose
- **Front-End** : Bootstrap ver. 5.2 (python lib: django-bootstrap5 ver. 23.1)
- **Back-End**  : `Django 4.2`, gunicorn, Nginx
- **DB**        : SQLite3 -> PostgreSQL 변경 예정


## 가이드
### Configure setting
초기 데이터 설정 - 관리자 계정, 그룹, 이메일 허용 초기 도메인
- app/.config_secret/init_dbdata.json
    - `auth.user`에서 password는 다음 코드를 사용해 반환 받은 값 삽입
    ```
    from django.contrib.auth.hashers import make_password
    make_password('your_password')
    ```
    - `auth.user`에서 groups는 user가 속한 그룹 목록이며, pk 값으로 그룹 구분
    ```
    "groups": [1, 2]
    ```
<details>
<summary>파일 내용</summary>

<!-- summary 아래 한칸 공백 두어야함 -->
```
[
  {
    "model": "estimate.registereddomain",
    "pk": 1,
    "fields": {
      "email": ""
    }
  },
  {
    "model": "auth.group",
    "pk": 1,
    "fields": {
      "name": "개발"
    }
  },
  {
    "model": "auth.group",
    "pk": 2,
    "fields": {
      "name": "영업"
    }
  },
  {
    "model": "auth.user",
    "pk": 1,
    "fields": {
      "username": "admin",
      "password": "",
      "is_superuser": true,
      "is_staff": true
    }
  },
  {
    "model": "auth.user",
    "pk": 2,
    "fields": {
      "username": "",
      "password": "",
      "is_staff": true,
      "email": ",
      "groups": [1, 2]
    }
  },
  {
    "model": "auth.user",
    "pk": 3,
    "fields": {
      "username": "",
      "password": "",
      "is_staff": false,
      "email": "",
      "groups": [2]
    }
  }
]
```
</details>


공통 설정 - 시크릿 키 및 적절한 공수산정 기준 입력
- app/.config_secret/settings_common.json
```
{
  "django": {
    "secret_key": "your_key",
    "init_scope_md": {
      "PC WEB": ,
      "Mobile WEB": ,
      "Android APP": ,
      "iOS APP": ,
      "관리자 WEB": ,
      "CS Program":
    },
    "screen_criteria_num": ,
    "url_criteria_num":
  }
}
```

개발 설정 - 허용 호스트, CSRF에 호스트 네임, AWS 키 정보 등록
- app/.config_secret/settings_debug.json
```
{
  "django": {
    "allowed_hosts": [
      "localhost",
      "127.0.0.1",
      ".compute.amazonaws.com",
    ],
    "csrf_trusted_origins": [
      "http://example.com",
      "https://example.com",
    ],
    "aws_access_key_id": "",
    "aws_secret_access_key": ""
  }
}
```

배포 설정 - 허용 호스트, CSRF에 호스트 네임, AWS 키 정보 등록
- app/.config_secret/settings_debug.json
```
{
  "django": {
    "allowed_hosts": ["*"],
    "csrf_trusted_origins": [
      "https://example.com",
    ],
    "aws_access_key_id": "",
    "aws_secret_access_key": ""
  }
}
```

### Dev env setting
스크립트 다운로드
```
$ ./setup.sh
```

docker-compose 실행: 코드 갱신 시 --build 옵션 사용
```
$ docker-compose -f docker-compose.dev.yml up -d --build
```

서비스 중지
```
$ docker-compose -f docker-compose.dev.yml down
```

기존 코드 실행
```
$ docker-compose -f docker-compose.dev.yml up -d
```

### Deploy env setting
docker-compose 실행: 코드 갱신 시 --build 옵션 사용
```
$ ./service_update.sh
```

서비스 중지
```
$ docker-compose -f docker-compose.yml down
```

기존 코드 실행
```
$ ./service_run.sh
```
