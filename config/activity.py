def log_activity(user, action):
	"""Rejistu atividade utilizadór iha tabel ACTIVITY_LOG (user_id, action, created_at)."""
	from users.models import ActivityLog
	if user is not None and getattr(user, 'is_authenticated', False):
		ActivityLog.objects.create(user=user, action=str(action)[:255])
