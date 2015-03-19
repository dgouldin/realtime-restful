import types
from collections import defaultdict
from functools import wraps
from urlparse import urljoin

from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse, NoReverseMatch


LIST_METHODS = ('POST',)
DETAIL_METHODS = ('PUT', 'PATCH', 'DELETE',)
ALL_METHODS = LIST_METHODS + DETAIL_METHODS


model_registry = defaultdict(list)


def register(methods, model):
    """
    Decorator for registering lookup functions. Modeled after django.dispatch.receiver.

    A lookup_func should return a fully qualified path.
    """
    def _decorator(lookup_func):
        model_registry[model].append((methods, lookup_func))
        return lookup_func
    return _decorator

def normalize_channel(path):
    "Strip off querystring and trailing slashes"
    return path.split('?', 1)[0].rstrip('/')

def find_urls(obj, method):
    "Utility to locate URLs that might include details of a given object"
    for methods, lookup_func in model_registry[type(obj)]:
        if method in methods:
            yield lookup_func(obj)


# helpers for generating common URLs
def empty(viewname):
    "For URLs that don't require any arguments at all"
    url = reverse(viewname)
    def _empty(obj):
        return url
    return _empty


def primary_key(viewname):
    "For URLs that accept a primary key as 'pk'"
    def _primary_key(obj):
        return reverse(viewname, kwargs={'pk': obj.pk})
    return _primary_key

def primary_key_filter(viewname):
    "For URLs that filter on the primary key field via a query param"
    def _primary_key_filter(obj):
        pk_field = obj.__class__._meta.pk.name
        return "{}?{}={}".format(reverse(viewname), pk_field, obj.pk)
    return _primary_key_filter


def foreign_key(viewname, fk_field_name):
    """
    For URLs that refer to an instance via a foreign key

    Accepts the name of the foreign key
    """
    def _foreign_key(obj):
        fk_field = obj.__class__._meta.get_field(fk_field_name)
        return reverse(viewname, kwargs={'pk': getattr(obj, fk_field.attname)})
    return _foreign_key


def generic_foreign_key(viewname, gfk_field_name, model):
    """
    For URLs that refer to an instance via a generic foreign key

    Accepts the name of the foreign key, and also the model this particular URL
    is associated with, since the foreign key can refer to multiple model types
    """

    def _generic_foreign_key(obj):
        content_type_id = ContentType.objects.get_for_model(model).id
        gfk_field = getattr(obj.__class__, gfk_field_name)
        ct_field = obj._meta.get_field(gfk_field.ct_field)

        if getattr(obj, ct_field.attname) == content_type_id:
            return reverse(viewname, kwargs={'pk': getattr(obj, gfk_field.fk_field)})
        # this should never happen
        raise NoReverseMatch('Unable to resolve generic foreign key for {}'.format(obj))

    return _generic_foreign_key
