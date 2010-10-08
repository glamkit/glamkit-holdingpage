Holdingpage
===========

Holding page app for Django projects.

.. rubric:: This is part of the GLAMkit Project. For more information, please visit http://glamkit.org.


Background
^^^^^^^^^^

The code for this app was inspired from:

* http://julienphalip.com/blog/2008/10/23/site-wide-login-protection-and-public-views/
* http://code.google.com/p/django-maintenancemode/

To switch the holding page on, add 'holdingpage' to your INSTALLED_APPS, and set the HOLDINGPAGE_ACTIVATED setting to True.

.. highlight:: python

You also need to add the holding page middleware in your settings, as high as possible in the list, for example::

    MIDDLEWARE_CLASSES = (
        'holdingpage.middleware.HoldingPageMiddleware',
        ...
    )

Remark: If you use 'django.contrib.auth.middleware.AuthenticationMiddleware', it's a good idea to put
'HoldingPageMiddleware' below in the list (as your hooks, for example, might need to have access to the user attribute in the
request object).

Then, by default, any URL and any view systematically redirects to the holding page.
Also by default, the holding page sits at the URL '/holding/'. To change that, you need to use the following setting, for example::
    
    HOLDINGPAGE_URL = '/'

There are several ways to declare exceptions (that is, cases where you do *not* want to redirect to the holding page):

1) Allowed url patterns:

    You can declare allowed url patterns (regular expressions) in two ways:

    a) From the settings:

    For example if you want to allow every page of the admin, use the following setting:
        HOLDINGPAGE_ALLOWED_URL_PATTERNS = ['^/admin(.*)$',]

    b) Dynamically in your code:

        from holdingpage import holdingpage_registry
        holdingpage_registry.allowed_url_patterns += [re.compile('^^/admin(.*)$'),]

2) Allowed views:

    There are also two ways for allowing views:

    a) From the settings:
    
        HOLDINGPAGE_ALLOWED_VIEWS = ['path.to.a.view',]

    b) Dynamically in your code:
    
        from holdingpage import holdingpage_registry
        from myapp.views import a_view
        holdingpage.allowed_views += [a_view,]

3) With a decorator:

    from holdingpage.decorators import allowed_view

    @allowed_view
    def a_view(request):
        return HttpResponse('Blah')

4) By adding a custom hook:

    
    a) From the settings:
    	
    	     HOLDINGPAGE_HOOKS = ['path.to.a.hook',]
    	
    	Note that some default hooks are already provided for your
        convenience in `holdingpage.hooks`, and therefore you can add them
        directly with the HOLDINGPAGE_ALLOWED_VIEWS.

    b) Dynamically in your code:

        For example, to allow staff members to access any part of the site:
    
            from holdingpage import holdingpage_registry
    
            def allow_staff(request):
                return (hasattr(request, 'user') and request.user.is_staff)
                
            holdingpage_registry.hooks += [allow_staff]
    
        Another example, to let the app play nicely with django-debugtoolbar:
    
            def allow_debugtoolbar_styles(request):
                return '__debug__' in request.get_full_path()
    
        You can of course combine several hooks into one, for example:
        
            def my_hook(request):
                if '__debug__' in request.get_full_path():
                    return True
                if (hasattr(request, 'user') and request.user.is_staff):
                    return True
                return False
            
        Note that if the hook returns True, then access will be allowed.
