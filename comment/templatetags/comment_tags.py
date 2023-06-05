from django import template

from ..models import Comment

register = template.Library()


@register.simple_tag
def get_latest_comments():
    return Comment.objects.all()[:10]
