from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404, get_list_or_404
from django.views.generic import DetailView
from django.views.generic.list import ListView

from comment.models import Comment
from .models import ArticlePost, Publicity
from .models import Category, Keyword, PagePost


class ArticleListView(ListView):
    template_name = 'article/list.html'
    context_object_name = 'article_list'
    model = ArticlePost
    page_type = ''
    page_kwarg = 'page'
    paginate_by = 5
    tag = None
    author = None
    category = None

    def get_queryset(self):
        queryset = self.model.objects.filter(publicity=Publicity.public)
        if category_slug := self.kwargs.get('category', ''):
            self.category = get_object_or_404(Category, slug=category_slug)
            queryset = queryset.filter(category=self.category)
        elif author_id := self.kwargs.get('author', ''):
            self.author = get_object_or_404(User, id=author_id)
            queryset = queryset.filter(author=self.author)
        elif tag_slug := self.kwargs.get('tag', ''):
            self.tag = get_object_or_404(Keyword, name=tag_slug)
            queryset = queryset.filter(keywords=self.tag)
        elif year := self.kwargs.get('year', 0):
            month = self.kwargs.get('month', 0)
            queryset = get_list_or_404(queryset, created__year=year, created__month=month)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['author'] = self.author
        context['tag'] = self.tag
        return context


class ArticleDetailView(DetailView):
    """
    文章详情页面
    """
    model = ArticlePost
    slug_url_kwarg = 'slug'
    context_object_name = 'article'
    template_name = 'article/detail.html'

    def get_object(self, **kwargs):
        obj = super().get_object(**kwargs)
        obj.body = obj.viewed()
        obj.update_views()
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comments = Comment.objects.filter(article=self.object.id)
        context['comments'] = comments
        context['reply_id'] = self.request.GET.get('reply')
        return context


class PageDetailView(ArticleDetailView):
    model = PagePost
    context_object_name = 'page'
    template_name = 'article/page.html'


class AllArticleRssFeed(Feed):
    # 显示在聚会阅读器上的标题
    title = settings.SITE_DESCRIPTION
    # 跳转网址，为主页
    link = "/"
    # 描述内容
    description = settings.SITE_DESCRIPTION

    # 需要显示的内容条目，这个可以自己挑选一些热门或者最新的博客
    @staticmethod
    def items():
        return ArticlePost.objects.all()[:100]

    # 显示的内容的标题,这个才是最主要的东西
    def item_title(self, item):
        return item.title

    # 显示的内容的描述
    def item_description(self, item):
        return item.viewed()

# class ArticleCreateView(CreateView):
#     model = ArticlePost
#
#     fields = '__all__'
#     # fields = ['title', 'body']
#
#     template_name = 'article/create_by_class_view.html'
#
#
# @login_required(login_url='/userprofile/login/')
# def article_update(request, pk: int):
#     """
#     更新文章的视图函数
#     通过POST方法提交表单，更新title、body字段
#     GET方法进入初始表单页面
#     pk： 文章的 id
#     """
#     article = ArticlePost.objects.get(id=pk)
#     if request.user != article.author:
#         return HttpResponse("抱歉，你无权修改这篇文章。")
#     if request.method == "POST":
#         article_post_form = ArticlePostForm(data=request.POST)
#         if article_post_form.is_valid():
#             article.title = request.POST['title']
#             article.body = request.POST['body']
#             article.save()
#             return redirect("article:article_detail", pk=pk)
#         return HttpResponse("表单内容有误，请重新填写。")
#     article_post_form = ArticlePostForm()
#     context = {'article': article, 'article_post_form': article_post_form}
#     return render(request, 'article/update.html', context)
#
#
# @login_required(login_url='/userprofile/login/')
# def article_create(request):
#     if not request.user.is_superuser:  # is_staff 或许更合适
#         return HttpResponse('只有管理员可以发表文章!')
#     if request.method == 'POST':
#         article_post_form = ArticlePostForm(data=request.POST)
#         if article_post_form.is_valid():
#             new_article = article_post_form.save(commit=False)
#             new_article.author = User.objects.get(id=request.user.id)
#             if request.POST['column'] != 'none':
#                 ...
#             new_article.save()
#             return redirect('article:article_list')
#         return HttpResponse('表单填写有误，请重新填写。')
#     article_post_form = ArticlePostForm()
#     # columns = ArticleColumn.objects.all()
#     context = {'article_post_form': article_post_form, 'columns': None}
#     return render(request, 'article/create.html', context)
#
#
# @login_required(login_url='/userprofile/login/')
# def article_safe_delete(request, pk: int):
#     if request.method != 'POST':
#         return HttpResponse("仅允许post请求")
#     article = ArticlePost.objects.get(id=pk)
#     if request.user != article.author:
#         return HttpResponse("抱歉，你无权修改这篇文章。")
#     article.delete()
#     return redirect('article:article_list')
