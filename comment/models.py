from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

from article.models import ArticlePost, PagePost


class Comment(models.Model):
    article = models.ForeignKey(
        ArticlePost,
        on_delete=models.CASCADE,
        related_name='comments',
        blank=True, null=True,
    )
    page = models.ForeignKey(
        PagePost,
        on_delete=models.CASCADE,
        related_name='comments',
        blank=True, null=True,
    )
    author = models.TextField(max_length=50, verbose_name='作者')
    body = models.TextField(verbose_name='内容')
    mail = models.EmailField(verbose_name='邮箱')
    url = models.URLField(blank=True, verbose_name='网站')
    ip = models.GenericIPAddressField(verbose_name='IP')
    agent = models.TextField(verbose_name='User-Agent')
    created = models.DateTimeField(auto_now_add=True, verbose_name='创建日期')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='replies')

    class Meta:
        verbose_name = '评论'
        verbose_name_plural = verbose_name
        ordering = ('-created',)

    def __str__(self):
        return self.body[:20]

    def get_absolute_url(self):
        if self.article:
            return reverse('article:article_detail', args=[self.article.slug])
        else:
            return reverse('article:page_detail', args=[self.page.slug])

    @property
    def children(self):
        return Comment.objects.filter(parent=self).order_by('-created').all()

    @property
    def is_parent(self):
        return self.parent is None

    def get_root(self):
        comm = self
        while True:
            if comm.is_parent:
                return comm
            else:
                comm = comm.parent
