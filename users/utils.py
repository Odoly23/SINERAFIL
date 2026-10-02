from django.contrib.auth.models import Group, User
from django.db import transaction

from users.models import EmpUser


@transaction.atomic
def save_emp_account(emp, username, group_name, password=None, is_active=True, email=None):
    """Kria ka atualiza konta User ba funcionariu (Emp) no tau iha grupu."""
    empuser = EmpUser.objects.filter(emp=emp).select_related('user').first()
    if empuser and empuser.user:
        user = empuser.user
    else:
        user = User()
    user.username = username
    user.email = email or emp.email or ''
    parts = (emp.name or '').strip().split(' ', 1)
    user.first_name = parts[0]
    user.last_name = parts[1] if len(parts) > 1 else ''
    user.is_active = is_active
    if password:
        user.set_password(password)
    elif not user.pk:
        user.set_unusable_password()
    user.save()
    user.groups.clear()
    user.groups.add(Group.objects.get_or_create(name=group_name)[0])
    if not empuser:
        EmpUser.objects.create(emp=emp, user=user)
    return user
