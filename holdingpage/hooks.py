
def allow_staff(request):
    ''' Allow access if the user doing the request is logged in and a staff member.'''
    return (hasattr(request, 'user') and request.user.is_staff)