import hashlib

from django import template

from ..models import ArticlePost, Category, PagePost

register = template.Library()


@register.simple_tag
def get_month_date():
    """获取文章发表的不同月份"""
    return ArticlePost.objects.datetimes('created', 'month', order='DESC')


@register.simple_tag
def get_latest_articles():
    return ArticlePost.objects.all()[:10]


@register.simple_tag
def get_categories():
    return Category.objects.all()


@register.simple_tag
def get_gravatar_url(email, size=40):
    return f'https://www.gravatar.com/avatar/{hashlib.md5(email.lower().encode()).hexdigest()}'


@register.simple_tag
def get_pages():
    return PagePost.objects.all()
