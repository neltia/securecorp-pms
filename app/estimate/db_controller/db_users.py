from django.contrib.auth.models import User, Group


# 그룹에 속한 사용자 이메일 목록 조회
def get_emails_ingroup(group_name):
    group = Group.objects.get(name=group_name)
    users = group.user_set.all()
    emails = [(user.username, user.email) for user in users]
    return emails


# 특정 그룹에 속한 사용자인지 확인
def is_member(group_name, user):
    group = Group.objects.get(name='영업')
    is_member = group.user_set.filter(id=user.id).exists()
    return is_member


# 사용자가 속한 그룹 목록 조회
def get_user_groups(user):
    groups = Group.objects.filter(user=user)
    return groups
