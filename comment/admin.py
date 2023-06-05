from django.contrib import admin
from article.admin import ExportCsvMixin
from .models import Comment

# 自定义管理站点的名称和URL标题
admin.site.site_header = '网站管理'
admin.site.site_title = '博客后台管理'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('id', 'author', 'created', 'article', 'page', 'body', 'mail', 'url', 'ip')
    actions = ['export_as_csv']