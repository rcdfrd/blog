from django.urls import path, include

from . import views

app_name = 'article'

urlpatterns = [
    path('', views.ArticleListView.as_view(), name='article_list'),
    path('archives/<str:slug>/', views.ArticleDetailView.as_view(), name='article_detail'),
    path('<str:slug>.html', views.PageDetailView.as_view(), name='page_detail'),
    path('category/<str:category>/', views.ArticleListView.as_view(template_name='article/archive.html'),
         name='list-category'),
    path('author/<int:author>/', views.ArticleListView.as_view(template_name='article/archive.html'),
         name='list-author'),
    path('tag/<str:tag>/', views.ArticleListView.as_view(template_name='article/archive.html'),
         name='list-tag'),
    path('date/<int:year>/<int:month>',
         views.ArticleListView.as_view(template_name='article/archive.html'),
         name='list-date'),
    path('search/', include('haystack.urls')),
    path('feed/', views.AllArticleRssFeed(), name='rss'),
    # path('article-create/', views.article_create, name='article_create'),
    # path('article-safe-delete/<int:pk>/', views.article_safe_delete, name='article_safe_delete'),
    # path('article-update/<int:pk>/', views.article_update, name='article_update'),
    # path('detail-view/<int:pk>/', views.ArticleDetailView.as_view(), name='detail_view'),
    # path('create-view/', views.ArticleCreateView.as_view(), name='create_view'),
]
