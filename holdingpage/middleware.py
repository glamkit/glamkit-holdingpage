import re

from django.views.generic.simple import direct_to_template
from django.core.urlresolvers import reverse, get_resolver, NoReverseMatch, Resolver404
from django.http import HttpResponseRedirect
from django.conf import settings



class HoldingPageMiddleware(object):
    
    def _matches_allowed_view(self, view):
        from holdingpage import holdingpage_registry
        if holdingpage_registry.allowed_views:
            for allowed_view in holdingpage_registry.allowed_views:
                if view == allowed_view:
                    return True
        return False

    def _matches_allowed_path(self, path):
        from holdingpage import holdingpage_registry
        if holdingpage_registry.allowed_url_patterns:
            for pattern in holdingpage_registry.allowed_url_patterns:
                if pattern.match(path) is not None:
                    return True
        return False
    
    def process_request(self, request):
        from holdingpage import holdingpage_registry
        from holdingpage.decorators import AllowedView
        
        # Allow access if middleware is not activated
        holdingpage_activated = getattr(settings, 'HOLDINGPAGE_ACTIVATED', False)
        if not holdingpage_activated:
            return None

        # Allow access if one of the hooks returns True
        for hook in holdingpage_registry.hooks:
            if hook(request):
                return None

        # See if the path matches a view
        try:
            view_func = get_resolver(None).resolve(request.get_full_path())[0]
            
            # Allow access if the view was decorated with the allowed_view decorator
            if isinstance(view_func, AllowedView):
                return None
            
            # Allow access if view is explicity allowed in settings
            if self._matches_allowed_view(view_func):
                return None

            # Allow access to allowed views, doh!
            if view_func in holdingpage_registry.allowed_views:
                return None

        except (NoReverseMatch, Resolver404): 
            pass    

        # Allow access if path is explicity allowed in settings
        if self._matches_allowed_path(request.path):
            return None        

        # Render holding page if the request is for the holding page itself
        if holdingpage_registry.holdinpage_url == request.get_full_path():
            return direct_to_template(request, template='holdingpage/holdingpage.html')

        # Redirect to holding page
        return HttpResponseRedirect(holdingpage_registry.holdinpage_url)