from django.urls import path

from . import views

app_name = 'comment'

urlpatterns = [
    # 发表评论
    path('article-comment/<str:slug>/', views.PostComment.as_view(source='article'),
         name='post_article_comment'),
    path('article-comment/<str:slug>/<int:p_comment_id>/', views.PostComment.as_view(source='article'),
         name='post_article_reply'),
    path('page-comment/<str:slug>/', views.PostComment.as_view(source='page'), name='post_page_comment'),
    path('page-comment/<str:slug>/<int:p_comment_id>/', views.PostComment.as_view(source='page'),
         name='post_page_reply'),

]
