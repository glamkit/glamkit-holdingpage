import os.path
import re

from django.test import TestCase
from django.test.client import Client
from django.template import TemplateDoesNotExist
from django.conf import settings
from django.core.management import call_command
from django.db.models.loading import load_app
from django.contrib.auth.models import User
from django.contrib.admin.sites import LOGIN_FORM_KEY


from holdingpage.middleware import HoldingPageMiddleware
from holdingpage.tests.testapp.views import another_view
from holdingpage.hooks import allow_staff
from holdingpage import holdingpage_registry



class HoldingPageMiddlewareTestCase(TestCase):
    urls = 'holdingpage.tests.urls'
    
    def setUp(self):
        # Install testapp
        self.old_INSTALLED_APPS = settings.INSTALLED_APPS
        settings.INSTALLED_APPS += ['holdingpage.tests.testapp']
        load_app('testapp')
        call_command('flush', verbosity=0, interactive=False)
        call_command('syncdb', verbosity=0, interactive=False)
        
        # Tweak settings
        if hasattr(settings, 'HOLDINGPAGE_ACTIVATED'):
            self.old_HOLDINGPAGE_ACTIVATED = settings.HOLDINGPAGE_ACTIVATED

        if 'holdingpage.middleware.HoldingPageMiddleware' not in settings.MIDDLEWARE_CLASSES:
            self.old_MIDDLEWARE_CLASSES = settings.MIDDLEWARE_CLASSES
            settings.MIDDLEWARE_CLASSES = list(settings.MIDDLEWARE_CLASSES) + ['holdingpage.middleware.HoldingPageMiddleware']
    
        if hasattr(settings, 'HOLDINGPAGE_ALLOWED_URL_PATTERNS'):
            self.old_HOLDINGPAGE_ALLOWED_URL_PATTERNS = settings.HOLDINGPAGE_ALLOWED_URL_PATTERNS
        settings.HOLDINGPAGE_ALLOWED_URL_PATTERNS = ['^/a_path/$']
        
        if hasattr(settings, 'HOLDINGPAGE_ALLOWED_VIEWS'):
            self.old_HOLDINGPAGE_ALLOWED_VIEWS = settings.HOLDINGPAGE_ALLOWED_VIEWS
        settings.HOLDINGPAGE_ALLOWED_VIEWS = ['holdingpage.tests.testapp.views.a_view']
    
        if hasattr(settings, 'HOLDINGPAGE_URL'):
            self.HOLDINGPAGE_URL = settings.HOLDINGPAGE_URL
        settings.HOLDINGPAGE_URL = '/holding-test/'
    
        # Initial Data
        self.notstaff_user = User.objects.create_user(username='notstaff', email='notstaff@example.org', password='test')
        self.staff_user = User.objects.create_user(username='staff', email='staff@example.org', password='test')
        self.staff_user.is_staff = True
        self.staff_user.save()
    
    def tearDown(self):
        # Restore settings
        if hasattr(settings, 'old_HOLDINGPAGE_ACTIVATED'):
            settings.HOLDINGPAGE_ACTIVATED = self.old_HOLDINGPAGE_ACTIVATED
        if hasattr(settings, 'old_HOLDINGPAGE_ALLOWED_URL_PATTERNS'):
            settings.HOLDINGPAGE_ALLOWED_URL_PATTERNS = self.old_HOLDINGPAGE_ALLOWED_URL_PATTERNS
        if hasattr(self, 'old_MIDDLEWARE_CLASSES'):
            settings.MIDDLEWARE_CLASSES = self.old_MIDDLEWARE_CLASSES
        if hasattr(self, 'old_HOLDINGPAGE_URL'):
            settings.HOLDINGPAGE_URL = self.old_HOLDINGPAGE_URL
        settings.INSTALLED_APPS = self.old_INSTALLED_APPS
    
    # Util functions --------------------------------------------------------
    
    def assertHoldingPage(self, url):
        response = self.client.get(url, follow=True)
        self.assertEquals(response.redirect_chain, [('http://testserver/holding-test/', 302)])
        self.assertContains(response, text='This is a holding page', count=1, status_code=200)
    
    def assertNormalPage(self, url):
        response = self.client.get(url)
        self.assertContains(response, text='Normal page', count=1, status_code=200)
    
    # Actual tests --------------------------------------------------------
    
    def test_disabled_middleware(self):
        "Explicitly disabling the HOLDINGPAGE_ACTIVATED should work"
        settings.HOLDINGPAGE_ACTIVATED = False
        self.assertNormalPage('/')
        
    def test_enabled_middleware(self):
        settings.HOLDINGPAGE_ACTIVATED = True
        self.assertHoldingPage('/')
        
    def test_view_hooks(self):
        old_hooks = holdingpage_registry.hooks # Back up old hooks
        settings.HOLDINGPAGE_ACTIVATED = True
        
        self.client.login(username='notstaff', password='test')
        self.assertHoldingPage('/')
        self.client.login(username='staff', password='test')
        self.assertHoldingPage('/')

        if hasattr(settings, 'HOLDINGPAGE_HOOKS'):
            self.old_HOLDINGPAGE_HOOKS = settings.HOLDINGPAGE_HOOKS
        settings.HOLDINGPAGE_HOOKS = ['holdingpage.hooks.allow_staff']
        holdingpage_registry.load_settings()

        self.client.login(username='notstaff', password='test')
        self.assertHoldingPage('/')
        self.client.login(username='staff', password='test')
        self.assertNormalPage('/')
        
        if hasattr(settings, 'old_HOLDINGPAGE_HOOKS'):
            settings.HOLDINGPAGE_HOOKS = self.old_HOLDINGPAGE_HOOKS
        holdingpage_registry.load_settings()
    
    def test_allowed_paths(self):
        old_paths = holdingpage_registry.allowed_url_patterns # Back up old paths
        settings.HOLDINGPAGE_ACTIVATED = True
        self.assertNormalPage('/a_path/') # Explicitly allowed in setUp above
        self.assertHoldingPage('/another_path/')
        
        holdingpage_registry.allowed_url_patterns = old_paths + [re.compile('^/another_path/$')]
        self.assertNormalPage('/another_path/')
        self.assertHoldingPage('/another_path/folder/')
        
        holdingpage_registry.allowed_url_patterns = old_paths + [re.compile('^/another_path(.*)$')]
        self.assertNormalPage('/another_path/')
        self.assertNormalPage('/another_path/folder/')
        
        holdingpage_registry.allowed_url_patterns = old_paths # Restore old paths
    
    def test_decorated_views(self):
        settings.HOLDINGPAGE_ACTIVATED = True
        self.assertNormalPage('/decorated/')
        self.assertHoldingPage('/not_decorated/')

    def test_allowed_views(self):
        old_views = holdingpage_registry.allowed_views # Back up old views
        settings.HOLDINGPAGE_ACTIVATED = True
        self.assertNormalPage('/a_view/') # Explicitly allowed in setUp above
        self.assertHoldingPage('/another_view/')
        
        holdingpage_registry.allowed_views = old_views + [another_view]
        self.assertNormalPage('/a_view/')
        self.assertNormalPage('/another_view/')
        
        holdingpage_registry.allowed_views = old_views # Restore old paths
