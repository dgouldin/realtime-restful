from __future__ import absolute_import
from rest_framework.viewsets import ModelViewSet
from .models import Todo

class TodoViewSet(ModelViewSet):
    model = Todo
    filter_fields = ('id',)
