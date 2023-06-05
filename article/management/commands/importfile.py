import json
import os
from datetime import datetime

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone
from article.models import ArticlePost, Category, Keyword, PagePost


class Command(BaseCommand):
    """
    向数据库中导入markdown文件
    """
    help = 'Insert blog data to database'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str)

    def handle(self, *args, **options):

        json_path = options['json_file'].replace('\\', '/')
        with open(json_path, 'r', encoding='utf-8') as f:
            f_json = json.load(f)
            f.close()
        for c in f_json.get('categories'):
            if not Category.objects.filter(slug=c.get('slug')).exists():
                if c.get('description'):
                    Category.objects.create(name=c.get('name'), slug=c.get('slug'), description=c.get('description'))
                else:
                    Category.objects.create(name=c.get('name'), slug=c.get('slug'))
        json_dir = os.path.dirname(json_path)
        for a in f_json.get('articles'):
            with open(os.path.join(json_dir, a.get('file')), 'r', encoding='utf-8') as f:
                body = f.read()
                f.close()
            title = a.get('title')
            if not title:
                print("Can't Find title in ", a)
                return
            b_time = datetime.strptime(a.get('date'), '%Y-%m-%d-%H:%M:%S')
            timestamp = timezone.make_aware(b_time)
            category = Category.objects.get(slug=a.get('category'))
            slug = a.get('slug')
            if ArticlePost.objects.filter(slug=slug).exists():
                continue
            article = ArticlePost(author=User.objects.get(id=1), created=timestamp, updated=timestamp,
                                  title=title, body=body, category=category, slug=slug)
            article.save()
            for k in a.get('keywords'):
                if not Keyword.objects.filter(name=k):
                    Keyword.objects.create(name=k)
                article.keywords.add(Keyword.objects.get(name=k))
            article.check()
            article.save()
        for p in f_json.get('pages'):
            title = p.get('title')
            b_time = datetime.strptime(p.get('date'), '%Y-%m-%d-%H:%M:%S')
            timestamp = timezone.make_aware(b_time)
            order = p.get('order')
            slug = p.get('slug')
            with open(os.path.join(json_dir, p.get('file')), 'r', encoding='utf-8') as f:
                body = f.read()
                f.close()
            if PagePost.objects.filter(slug=slug).exists():
                continue
            PagePost.objects.create(author=User.objects.get(id=1), created=timestamp, updated=timestamp,
                                    title=title, body=body, order=order, slug=slug)

        self.stdout.write('Successfully insert blog data')
