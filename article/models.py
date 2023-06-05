import mistune
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _
from pygments import highlight
from pygments.formatters import html
from pygments.lexers import get_lexer_by_name


class HighlightRenderer(mistune.HTMLRenderer):
    def block_code(self, code, info=None):
        if info:
            lexer = get_lexer_by_name(info, stripall=True)
            formatter = html.HtmlFormatter()
            return highlight(code, lexer, formatter)
        return f'<pre><code>{mistune.escape(code)}</code></pre>'


class Category(models.Model):
    # 分类名字
    name = models.CharField('文章分类', max_length=20)
    # slug 用作分类路径，对一无二
    slug = models.SlugField(unique=True)
    # 分类栏目页描述
    description = models.TextField('描述', max_length=240, default=settings.SITE_DESCRIPTION,
                                   help_text='用来作为SEO中description,长度参考SEO标准')

    class Meta:
        verbose_name = '分类'
        verbose_name_plural = verbose_name
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('article:page_detail', kwargs={'slug': self.slug, })

    def get_article_list(self):
        return ArticlePost.objects.filter(category=self)


class Keyword(models.Model):
    name = models.CharField('文章关键词', max_length=20, unique=True)

    class Meta:
        verbose_name = '关键词'
        verbose_name_plural = verbose_name
        ordering = ['name']

    def __str__(self):
        return self.name


class Publicity(models.TextChoices):
    public = 'public', _('公开')
    hide = 'hide', _('隐藏')
    protected_by_password = 'password', _('密码保护')
    private = 'private', _('私密')
    awaiting = 'awaiting', _('等待审核')


class ArticlePost(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='作者')
    title = models.CharField(max_length=100, verbose_name='文章标题')
    body = models.TextField(verbose_name='文章内容')
    excerpt = models.CharField(max_length=300, blank=True, verbose_name='文章摘要', help_text='自动生成')
    created = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    updated = models.DateTimeField(auto_now=True, verbose_name='修改时间')
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(Category, verbose_name='文章分类', on_delete=models.RESTRICT)
    keywords = models.ManyToManyField(Keyword, verbose_name='文章关键词',
                                      help_text='文章关键词，用来作为SEO中keywords，最好使用长尾词，3-4个足够')
    publicity = models.CharField(max_length=10, choices=Publicity.choices, default=Publicity.public,
                                 verbose_name='公开度')
    password = models.CharField(max_length=20, blank=True, null=True, default='', verbose_name='文章密码')
    total_views = models.PositiveIntegerField(default=0, verbose_name='阅览量')
    allow_comment = models.BooleanField(default=True, verbose_name='允许评论')

    def save(self, *args, **kwargs):
        if kwargs.get('update_fields') == ['total_views']:
            super().save(*args, **kwargs)
            return
        self.updated = timezone.now()
        self.excerpt = strip_tags(self.viewed())[:200]
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = '文章'
        verbose_name_plural = verbose_name
        ordering = ('-created',)  # '-created' 表明数据应该以倒序排列

    def __str__(self):
        return self.title

    def viewed(self):
        md = mistune.create_markdown(renderer=HighlightRenderer(),
                                     plugins=['strikethrough', 'table', 'url', 'task_lists'])
        return md(self.body)

    def get_pre(self):
        return ArticlePost.objects.filter(id__lt=self.id).order_by('-id').first()

    def get_next(self):
        return ArticlePost.objects.filter(id__gt=self.id).order_by('id').first()

    def get_absolute_url(self):
        return reverse('article:page_detail', kwargs={'slug': self.slug})

    def update_views(self):
        self.total_views += 1
        self.save(update_fields=['total_views'])


class PagePost(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='作者')
    title = models.CharField(max_length=100, verbose_name='文章标题')
    body = models.TextField(verbose_name='文章内容')
    created = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    updated = models.DateTimeField(auto_now=True, verbose_name='修改时间')
    slug = models.SlugField(unique=True)
    order = models.IntegerField(unique=True, verbose_name='页面顺序')
    publicity = models.CharField(max_length=10, choices=Publicity.choices, default=Publicity.public,
                                 verbose_name='公开度')
    password = models.CharField(max_length=20, blank=True, null=True, verbose_name='文章密码')
    total_views = models.PositiveIntegerField(default=0, verbose_name='阅览量')
    allow_comment = models.BooleanField(default=True, verbose_name='允许评论')

    def save(self, *args, **kwargs):
        if kwargs.get('update_fields') == ['total_views']:
            super().save(*args, **kwargs)
            return
        self.updated = timezone.now()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = '独立页面'
        verbose_name_plural = verbose_name
        ordering = ('order', '-created')

    def __str__(self):
        return self.title

    def viewed(self):
        md = mistune.create_markdown(renderer=HighlightRenderer(),
                                     plugins=['strikethrough', 'table', 'url', 'task_lists'])
        return md(self.body)

    def update_views(self):
        self.total_views += 1
        self.save(update_fields=['total_views'])
