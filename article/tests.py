from django.test import Client, RequestFactory, TestCase
from django.contrib.auth.models import User
from .models import ArticlePost, Tags
from django.urls import reverse


class ArticleTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()

    def test_validate_article(self):
        user = User.objects.get_or_create(
            email="test@gmail.com",
            username="test")[0]
        user.set_password("test")
        user.is_staff = True
        user.is_superuser = True
        user.save()

        tag = Tags()
        tag.name = "nicetag"
        tag.save()


        article = ArticlePost()
        article.title = "nicetitle"
        article.body_md = "nicecontent"
        article.author = user
        article.status = 'public'
        article.slug = '999'
        article.save()
        self.assertEqual(0, article.tags.count())
        article.tags.add(tag)
        article.save()

        artile_privacy = ArticlePost()
        artile_privacy.title = "nicetitle"
        artile_privacy.body_md = "nicecontent"
        artile_privacy.author = user
        artile_privacy.status = 'private'
        artile_privacy.slug = '888'
        artile_privacy.save()

        self.assertEqual(1, article.tags.count())

        response = self.client.get(article.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        response = self.client.get(tag.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('article:list'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/posts')
        self.assertEqual(response.status_code, 200)

        response = self.client.get(artile_privacy.get_absolute_url())
        self.assertEqual(response.status_code, 200)
