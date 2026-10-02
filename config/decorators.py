from functools import wraps

from django.shortcuts import redirect, render

from config.auth_utils import get_group


def unauthenticated_user(view_func):
	@wraps(view_func)
	def wrapper_func(request, *args, **kwargs):
		if request.user.is_authenticated:
			return redirect('home')
		else:
			return view_func(request, *args, **kwargs)
	return wrapper_func


def allowed_users(allowed_roles=[]):
	def decorator(view_func):
		@wraps(view_func)
		def wrapper_func(request, *args, **kwargs):
			group = get_group(request.user)
			if group in allowed_roles:
				return view_func(request, *args, **kwargs)
			else:
				return render(request, 'auth/404.html', status=403)
		return wrapper_func
	return decorator
