from django.conf import settings
from django.core.cache import cache


def processor(requests):
    key = 'seo_processor'
    value = cache.get(key)
    if not value:
        value = {
            'SITE_NAME': settings.SITE_NAME,
            'SITE_DESCRIPTION': settings.SITE_DESCRIPTION,
            'TITLE': settings.SITE_NAME,
            'SITE_COPYRIGHT': settings.SITE_COPYRIGHT,
        }
        cache.set(key, value, 60 * 60 * 10)
    return value
