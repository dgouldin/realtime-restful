from django.conf.urls import patterns, include, url
from rest_framework.routers import DefaultRouter

from api import views as api_views

router = DefaultRouter(trailing_slash=False)
router.register('todos', api_views.TodoViewSet)
urlpatterns = router.urls
from django.shortcuts import redirect
urlpatterns += (
    url('todos/', lambda r: redirect('/api/todos', permanent=True)),
)
