from users.models import Emp


def get_group(user):
	"""Naran grupu (papél) utilizadór: admin / mekaniku / nain. Superuser = admin."""
	if not user.is_authenticated:
		return None
	group = user.groups.first()
	if group:
		return group.name
	return 'admin' if user.is_superuser else None


def get_emp(user):
	"""Funcionariu (Emp) ne'ebé liga ho utilizadór; None se la iha."""
	if not user.is_authenticated:
		return None
	return Emp.objects.filter(account__user=user).first()
