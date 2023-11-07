import html

import mistletoe
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _
from mistletoe import block_token
from mistletoe.html_renderer import HTMLRenderer
from mistletoe.latex_renderer import LaTeXRenderer
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import get_lexer_by_name as get_lexer, guess_lexer
from pygments.styles import get_style_by_name as get_style


class PygmentsRenderer(HTMLRenderer, LaTeXRenderer):
    formatter = HtmlFormatter()
    formatter.noclasses = True
    formatter.nowrap = True

    def __init__(self, *extras, style='default'):
        super().__init__(*extras)
        self.formatter.style = get_style(style)

    def render_math(self, token):
        if token.content.startswith('$'):
            return self.render_raw_text(token)
        return '${}$'.format(self.render_raw_text(token))

    def render_block_code(self, token: block_token.BlockCode) -> str:
        code = token.content
        lexer = get_lexer(token.language) if token.language else guess_lexer(code)
        template = '<pre><code{attr}>{inner}</code></pre>'
        if token.language:
            attr = f' class="language-{html.escape(token.language)}"'
        else:
            attr = ''
        inner = highlight(code, lexer, self.formatter)

        return template.format(attr=attr, inner=inner)


class Tags(models.Model):
    name = models.CharField(verbose_name=u'文章标签', max_length=20)

    class Meta:
        verbose_name = '标签'
        verbose_name_plural = verbose_name
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('article:list_tag', kwargs={'tag': self.name})


class Publicity(models.TextChoices):
    public = 'public', _('公开')
    hide = 'hide', _('隐藏')
    protected_by_password = 'password', _('密码保护')
    private = 'private', _('私密')
    awaiting = 'awaiting', _('等待审核')


class ArticlePost(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='作者')
    title = models.CharField(max_length=100, verbose_name='文章标题')
    body_md = models.TextField(verbose_name='文章 markdown 文本', blank=True, null=True)
    body = models.TextField(verbose_name='文章内容', blank=True)
    excerpt = models.CharField(max_length=300, blank=True, verbose_name='文章摘要', help_text='自动生成')
    created = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    updated = models.DateTimeField(auto_now=True, verbose_name='修改时间')
    slug = models.SlugField(unique=True)
    tags = models.ManyToManyField(Tags, verbose_name='文章标签', blank=True)
    publicity = models.CharField(max_length=10, choices=Publicity.choices, default=Publicity.public,
                                 verbose_name='公开度')
    password = models.CharField(max_length=20, blank=True, null=True, default='', verbose_name='文章密码')
    total_views = models.PositiveIntegerField(default=0, verbose_name='阅览量')
    allow_comment = models.BooleanField(default=True, verbose_name='允许评论')
    is_page = models.BooleanField(default=False, verbose_name='是否为主题页')

    def save(self, *args, **kwargs):
        if kwargs.get('update_fields') == ['total_views']:
            super().save(*args, **kwargs)
            return
        self.updated = timezone.now()
        self.body = self.viewed()
        self.excerpt = strip_tags(html.unescape(self.body))[:200]
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = '文章'
        verbose_name_plural = verbose_name
        ordering = ('-created',)  # '-created' indicates data arranged in reverse order

    def __str__(self):
        return self.title

    def viewed(self):
        if self.body_md:
            return PygmentsRenderer().render(mistletoe.Document(self.body_md))
        else:
            return self.body

    def get_pre(self):
        return ArticlePost.objects.filter(id__lt=self.id).order_by('-id').first()

    def get_next(self):
        return ArticlePost.objects.filter(id__gt=self.id).order_by('id').first()

    def update_views(self):
        self.total_views += 1
        self.save(update_fields=['total_views'])

    def get_absolute_url(self):
        return reverse('article:detail', kwargs={'slug': self.slug})

    def get_absolute_url_(self):
        return reverse('article:detail_', kwargs={'slug': self.slug})
