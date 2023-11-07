from django.urls import path

from . import views

app_name = 'article'

urlpatterns = [path('', views.ArticleListView.as_view(), name='list'),
               path('page/<int:page>/', views.ArticleListView.as_view(), name='list_page'),
               path('archives/<str:slug>', views.ArticleDetailView.as_view(), name='detail'),
               path('archives/<str:slug>/', views.ArticleDetailView.as_view(), name='detail_'),
               path('tags/<tag>/', views.TagListView.as_view(), name='list_tag'),
               path('posts', views.AllPostsView.as_view(), name='all_posts'),
               path('<slug>.html', views.ArticleDetailView.as_view(), name='page_detail'),
               path('feed/', views.ArticleRssFeed(), name='rss'),

               path('<slug>/', views.ArticleDetailView.as_view(), name='page_detail_'),
               ]
