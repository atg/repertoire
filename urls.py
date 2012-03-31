from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'repertoire.ui.views.home', name='home'),

    url(r'^artist/add$', 'repertoire.ui.views.add_artist', name='add_artist'),
    url(r'^artist/([^/]+)$', 'repertoire.ui.views.view_artist'),
    # url(r'^repertoire/', include('repertoire.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
