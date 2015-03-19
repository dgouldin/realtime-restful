from __future__ import absolute_import
from .url_registry import (
    LIST_METHODS,
    DETAIL_METHODS,
    register,
    primary_key,
    primary_key_filter,
)
from .models import Todo

register(DETAIL_METHODS, Todo)(primary_key('todo-detail'))
register(LIST_METHODS, Todo)(primary_key_filter('todo-list'))
