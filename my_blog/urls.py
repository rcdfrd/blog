from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('article.urls', namespace='article')),
    path('admin/', admin.site.urls),
    path('comment/', include('comment.urls', namespace='comment')),
    path('userprofile/', include('userprofile.urls', namespace='userprofile')),
    path('mdeditor/', include('mdeditor.urls')),
]

if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
