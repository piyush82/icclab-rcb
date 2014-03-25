from django.conf.urls import patterns, include, url
from django.contrib.auth.views import login, logout

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mysite.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page' : '/accounts/login'}),
    (r'^$', 'main_menu.views.index'),
    (r'^index/$', 'main_menu.views.index'),
    (r'^admin_page/$', 'main_menu.views.admin_page'),
    (r'^user_page/$', 'main_menu.views.user_page'),
    (r'^auth_token/$', 'main_menu.views.auth_token'),
    (r'^token_data/$', 'main_menu.views.token_data'),
    #(r'^/define_pricing/?ct=(?P<ct>\d+)/$', 'main_menu.views.define_pricing'),
    (r'^define_pricing/(?P<ct>\d+)/$', 'main_menu.views.define_pricing'),
)
