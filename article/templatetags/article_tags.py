from django import template

from ..models import ArticlePost

register = template.Library()


@register.simple_tag
def get_pages():
    return ArticlePost.objects.filter(is_page=True)
