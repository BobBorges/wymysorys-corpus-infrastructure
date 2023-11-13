from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
import functools




def user_has_permissions_assignment(view_func, redirect_url='nwymc-landing'):
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if hasattr(request.user, 'permission'):
            return view_func(request, *args, **kwargs)
        messages.warning(request, _('Your user instance has not been assigned any permissions level to access this resource. If you think you should have or want to have access, get in touch with the site administrator(s).'))
        return redirect(redirect_url)
    return wrapper




def user_is_at_least_contributor(view_func, redirect_url='nwymc-landing'):
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.permission.level != 'public':
            return view_func(request, *args, **kwargs)
        messages.warning(request, _("You're not authorized to see that."))
        return redirect(redirect_url)
    return wrapper




def user_is_at_least_worker(view_func, redirect_url='nwymc-landing'):
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.permission.level == 'worker' or request.user.permission.level == 'admin':
            return view_func(request, *args, **kwargs)
        messages.warning(request, _("You're not authorized to see that."))
        return redirect(redirect_url)
    return wrapper
