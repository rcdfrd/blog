import csv

from django.contrib import admin
from django.db import models
from django.http import HttpResponse
from mdeditor.widgets import MDEditorWidget

from .models import ArticlePost, Category, Keyword, PagePost

# 自定义管理站点的名称和URL标题
admin.site.site_header = '网站管理'
admin.site.site_title = '博客后台管理'


class ExportCsvMixin(object):
    def export_as_csv(self, request, queryset):
        meta = self.model._meta  # 用于确定导出的文件名, 格式为: app名.模型类名
        field_names = [field.name for field in meta.fields]  # 所有属性名
        response = HttpResponse(content_type='text/csv')  # 指定响应内容类型
        response['Content-Disposition'] = f'attachment; filename={meta}.csv'
        response.charset = 'utf-8-sig'  # 可选, 修改编码为带BOM的utf-8格式(Excel打开不会有乱码)
        writer = csv.writer(response, quoting=csv.QUOTE_ALL)
        writer.writerow(field_names)  # 将属性名写入csv
        for obj in queryset:  # 遍历要导出的对象列表
            writer.writerow([getattr(obj, field) for field in field_names])  # 遍历要导出的对象列表
        return response

    export_as_csv.short_description = '导出CSV'


@admin.register(ArticlePost)
class ArticleAdmin(admin.ModelAdmin, ExportCsvMixin):
    # 这个的作用是给出一个筛选机制，一般按照时间比较好
    date_hierarchy = 'created'
    # exclude = ('excerpt',)
    # 在查看修改的时候显示的属性，第一个字段带有<a>标签，所以最好放标题
    list_display = ('id', 'title', 'author', 'created', 'updated', 'publicity',)
    # 设置需要添加<a>标签的字段
    list_display_links = ('title',)
    # 激活过滤器，这个很有用
    list_filter = ('created', 'category')
    list_per_page = 50  # 控制每页显示的对象数量，默认是100
    filter_horizontal = ('keywords',)  # 给多选增加一个左右添加的框
    actions = ['export_as_csv']

    formfield_overrides = {
        models.TextField: {'widget': MDEditorWidget}
    }

    def get_queryset(self, request):
        qs = super(ArticleAdmin, self).get_queryset(request)
        return qs if request.user.is_superuser else qs.filter(author=request.user)


@admin.register(PagePost)
class PageAdmin(admin.ModelAdmin, ExportCsvMixin):
    # 这个的作用是给出一个筛选机制，一般按照时间比较好
    date_hierarchy = 'created'
    list_display = ('id', 'title', 'author', 'created', 'updated', 'publicity',)
    # 设置需要添加<a>标签的字段
    list_display_links = ('title',)
    # 激活过滤器，这个很有用
    list_filter = ('created',)
    list_per_page = 50  # 控制每页显示的对象数量，默认是100
    actions = ['export_as_csv']

    formfield_overrides = {
        models.TextField: {'widget': MDEditorWidget}
    }

    def get_queryset(self, request):
        qs = super(PageAdmin, self).get_queryset(request)
        return qs if request.user.is_superuser else qs.filter(author=request.user)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'slug')


@admin.register(Keyword)
class KeywordAdmin(admin.ModelAdmin):
    list_display = ('name', 'id')
