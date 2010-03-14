try:
    from functools import update_wrapper
except ImportError:
    from django.utils.functional import update_wrapper  # Python 2.3, 2.4 fallback.


def allowed_view(view_func):
    """
    Decorator which marks the given view as allowed (no redirection to holding page).
    """
    return AllowedView(view_func)


class AllowedView(object):
    def __init__(self, view_func):
        self.view_func = view_func
        update_wrapper(self, view_func)
        
    def __get__(self, obj, cls=None):
        view_func = self.view_func.__get__(obj, cls)
        return AllowedView(view_func)
    
    def __call__(self, request, *args, **kwargs):
        return self.view_func(request, *args, **kwargs)