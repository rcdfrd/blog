from datetime import datetime

from django.conf import settings
from django.contrib.syndication.views import Feed
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import ListView, DetailView

from .models import ArticlePost


class ArticleListView(ListView):
    template_name = 'index.html'
    context_object_name = 'article_list'
    model = ArticlePost
    page_type = ''
    page_kwarg = 'page'
    paginate_by = 3

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        queryset = super().get_queryset().filter(is_page=False)
        queryset = queryset.filter(publicity='public') | queryset.filter(publicity='password')

        return queryset


class TagListView(ArticleListView):
    template_name = 'posts.html'
    paginate_by = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['PAGE_TITLE'] = f'Entries tagged - "{self.kwargs.get("tag")}"'
        return context

    def get_queryset(self):
        tag = self.kwargs.get('tag')
        queryset = super().get_queryset().filter(is_page=False, tags__name=tag)
        queryset = queryset.filter(publicity='public') | queryset.filter(publicity='password')
        return queryset


class AllPostsView(ArticleListView):
    template_name = 'posts.html'
    paginate_by = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['PAGE_TITLE'] = 'All articles'
        return context


class ArticleDetailView(DetailView):
    model = ArticlePost
    slug_url_kwarg = 'slug'
    context_object_name = 'article'
    template_name = 'detail.html'

    def get_object(self, **kwargs):
        obj = super().get_object(**kwargs)
        obj.update_views()

        return obj

    def get_context_data(self, **kwargs):
        if self.request.user.is_superuser:
            return super().get_context_data(**kwargs)
        if self.object.publicity == 'private':
            self.object.body = 'Sorry, this article is private.'
            self.object.title = 'Sorry, this article is private.'
            self.object.created = datetime.fromtimestamp(0)
            self.object.tags.set([])

        if self.object.publicity == 'password':
            if not (self.request.COOKIES.get('password', None) == self.object.password or self.request.GET.get(
                    'password', None) == self.object.password):
                self.object.body = (f"""
            <form class="protected" action="{self.object.get_absolute_url_()}" method="get">
            <p class="word"> Please enter the password to view this article. </p>
            <p><input type="password" class="text" name="password" />
            <input type="submit" class="submit" value="Submit" /></p> </form>
            """)
            elif self.request.GET.get('password', None) == self.object.password:
                self.object.body = "<script> location.reload(); </script>"

        return super().get_context_data(**kwargs)

    def render_to_response(self, context, **response_kwargs):
        response = super().render_to_response(context, **response_kwargs)
        if self.request.GET.get('password', None) == self.object.password and self.object.publicity == 'password':
            if self.request.COOKIES.get('password', None) != self.object.password:
                response.set_cookie('password', self.object.password, max_age=60 * 60 * 24)
            else:
                return redirect(reverse('article:detail', kwargs={"slug": self.object.slug}))
        return response


class ArticleRssFeed(Feed):
    title = settings.SITE_NAME
    link = "/"
    description = settings.SITE_DESCRIPTION

    @staticmethod
    def items():
        return ArticlePost.objects.all()[:100]

    def item_title(self, item: ArticlePost):
        return item.title

    def item_description(self, item: ArticlePost):
        return item.excerpt
