from django.contrib import admin
from .models import ArticlePost, Tags


@admin.register(ArticlePost)
class ArticleAdmin(admin.ModelAdmin):
    date_hierarchy = 'created'
    exclude = ('excerpt',)
    list_display = ('id', 'title', 'author', 'created', 'updated', 'publicity',)
    list_display_links = ('title', )
    list_filter = ('created', )
    list_per_page = 100
    filter_horizontal = ('tags',)

    def get_queryset(self, request):
        qs = super(ArticleAdmin, self).get_queryset(request)
        return qs if request.user.is_superuser else qs.filter(author=request.user)


admin.site.register(Tags)