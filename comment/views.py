from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views import View

from article.models import PagePost
from .forms import CommentForm
from .models import ArticlePost
from .models import Comment


class PostComment(View):
    source = ''

    def post(self, request, slug, p_comment_id: int = None, *args, **kwargs):
        comment_form = CommentForm(request.POST)
        if not comment_form.is_valid():
            return HttpResponse("表单内容有误，请重新填写。")
        new_comment = comment_form.save(commit=False)
        # 过滤 垃圾评论 (暂时过滤全部url)
        if 'http' in new_comment.body:
            return HttpResponse("请勿在评论中包含url。")
        if self.source == 'article':
            article = get_object_or_404(ArticlePost, slug=slug)
            new_comment.article = article
        else:
            page = get_object_or_404(PagePost, slug=slug)
            new_comment.page = page
        if p_comment_id:
            parent_comment = Comment.objects.get(id=p_comment_id)
            new_comment.parent_id = parent_comment.get_root().id
        new_comment.ip = x_forwarded_for.split(',')[-1] if (
            x_forwarded_for := request.META.get('HTTP_X_FORWARDED_FOR')) else request.META.get('REMOTE_ADDR')
        new_comment.agent = request.META.get('HTTP_USER_AGENT')
        new_comment.save()
        if self.source == 'article':
            return redirect("article:article_detail", slug=slug)
        else:
            return redirect("article:page_detail", slug=slug)

    @staticmethod
    def get(request, *args, **kwargs):
        return HttpResponse("表单内容有误，请重新填写。")
