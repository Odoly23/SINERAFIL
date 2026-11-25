def get_role(user):
	"""Papél utilizadór (kolun `role` iha tabel USER): admin / technician / owner."""
	if not user.is_authenticated:
		return None
	return user.role
