from django.conf.urls.defaults import *
from django.conf import settings


urlpatterns = patterns('',
    url(r'^$', 'holdingpage.tests.testapp.views.index'),
    url(r'^a_path/', 'holdingpage.tests.testapp.views.a_view'),
    url(r'^another_path/', 'holdingpage.tests.testapp.views.another_view'),
    url(r'^another_path/folder/', 'holdingpage.tests.testapp.views.index'),
    url(r'^decorated/', 'holdingpage.tests.testapp.views.decorated_view'),
    url(r'^not_decorated/', 'holdingpage.tests.testapp.views.not_decorated_view'),
    url(r'^a_view/', 'holdingpage.tests.testapp.views.a_view'),
    url(r'^another_view/', 'holdingpage.tests.testapp.views.another_view'),
)
