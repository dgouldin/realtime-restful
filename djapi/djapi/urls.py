from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    # ... snip ...
    url(r'^api/', include('api.urls')),
)
