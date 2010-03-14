import re
from django.conf import settings

class AlreadyRegistered(Exception):
    pass


class HoldingPageRegistry(object):

    def __init__(self):
        self._reset()
    
    def _reset(self):
        self.holdinpage_url = '/holding'
        self.allowed_views = []
        self.allowed_url_patterns = []
        self.hooks = []

    def load_settings(self):
        self._reset()
        self.holdinpage_url = getattr(settings, 'HOLDINGPAGE_URL', self.holdinpage_url)
        
        if hasattr(settings, 'HOLDINGPAGE_ALLOWED_VIEWS'):
            for view_path in settings.HOLDINGPAGE_ALLOWED_VIEWS:
                view = self._get_callback(view_path)
                self.allowed_views.append(view)
                
        if hasattr(settings, 'HOLDINGPAGE_ALLOWED_URL_PATTERNS'):
            for url_pattern in settings.HOLDINGPAGE_ALLOWED_URL_PATTERNS:
                self.allowed_url_patterns.append(re.compile(url_pattern))
        
        if hasattr(settings, 'HOLDINGPAGE_HOOKS'):
            for hook_path in settings.HOLDINGPAGE_HOOKS:
                hook = self._get_callback(hook_path)
                self.hooks.append(hook)

    def _get_callback(self, callback_path):
        i = callback_path.rfind('.')
        module_path, callback_name = callback_path[:i], callback_path[i+1:]
        module = __import__(module_path, globals(), locals(), [callback_name])
        return getattr(module, callback_name)

holdingpage_registry = HoldingPageRegistry()
holdingpage_registry.load_settings()