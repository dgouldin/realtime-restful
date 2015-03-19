from __future__ import absolute_import

import json
import redis
import structlog
from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse, resolve, Resolver404
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.http import QueryDict
from django.utils.functional import SimpleLazyObject
from django.test import RequestFactory

from rest_framework.request import Request

from .url_registry import find_urls, normalize_channel

redis_client = redis.from_url(settings.REDIS_URL)
logger = structlog.get_logger('api')

def _request_factory():
    return RequestFactory(**{
        'SERVER_NAME': settings.SITE.name,
        'SERVER_PORT': settings.SITE.port,
        'wsgi.url_scheme': settings.SITE.scheme,
    })
request_factory = SimpleLazyObject(_request_factory)

fernet = Fernet(settings.FERNET_SECRET)


@receiver(post_save)
def handle_post_save(sender, instance, *args, **kwargs):
    method = 'POST' if kwargs.get('created', False) else 'PUT'
    for path in find_urls(instance, method):
        if '?' in path:
            path, querystring = path.split('?', 1)
            query = QueryDict(querystring)
        else:
            query = QueryDict('')
        method_channel = '{} {}'.format(method, path)
        if has_subscribers(method_channel):
            try:
                view_func, view_args, view_kwargs = resolve(path)
            except Resolver404:
                logger.warn('Could not resolve view for pubsub path',
                            path=path, method=method, instance=instance)

            request = request_factory.get(path, data=query)
            # Force DRF to use our User for its auth
            request._force_auth_user = User(is_staff=True)
            response = view_func(request, *view_args, **view_kwargs).render()
            if response.status_code == 200:
                redis_publish(method_channel, response.content)
            else:
                logger.warn('Received bad status code in pubusb API response',
                            path=path, method=method, instance=instance,
                            status_code=response.status_code)


@receiver(post_delete)
def handle_post_delete(sender, instance, *args, **kwargs):
    for path in find_urls(instance, 'DELETE'):
        method_channel = 'DELETE {}'.format(path)
        if has_subscribers(method_channel):
            redis_publish(method_channel, json.dumps(None))


def has_subscribers(channel):
    channel = normalize_channel(channel)
    num_subscribers = int(redis_client.execute_command('PUBSUB', 'NUMSUB',
                                                       channel)[1])
    return num_subscribers > 0


def redis_publish(channel, message):
    channel = normalize_channel(channel)
    secure_message = fernet.encrypt(message.encode('utf-8'))
    redis_client.publish(channel, secure_message)
