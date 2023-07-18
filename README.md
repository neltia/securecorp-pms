# Securecorp-PMS
시큐어코퍼 사 소속으로 개발한 프로젝트 관리 시스템
<br>
3단계 구성으로 회사 운영 업무를 자동화하고 적절한 공수를 산정하기 위함
- 1단계: 견적관리 -> 2단계: 프로젝트 진행관리 -> 3단계: 산출물 관리


## 프로젝트 소개
시큐어코퍼 사 소속으로 1인 개발한 프로젝트 관리 시스템 중 1단계, 견적관리에서 비즈니스 로직을 제거한 공개용 저장소입니다.

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
