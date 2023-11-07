import json
import os
from datetime import datetime

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from article.models import ArticlePost, Tags


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
            slug = a.get('slug')
            is_page = a.get('is_page') or False
            publicity = a.get('publicity') or 'public'
            if ArticlePost.objects.filter(slug=slug).exists():
                ArticlePost.objects.filter(slug=slug).update(author=User.objects.get(id=1), created=timestamp,
                                                             updated=timestamp, title=title, body_md=body,
                                                             is_page=is_page, publicity=publicity)
                ArticlePost.objects.filter(slug=slug).first().save()
                continue
            article = ArticlePost(author=User.objects.get(id=1), created=timestamp, updated=timestamp,
                                  title=title, body_md=body, slug=slug, is_page=is_page, publicity=publicity)
            article.save()
            if not a.get('tags'):
                article.check()
                article.save()
                continue
            for tag in a.get('tags'):
                if not Tags.objects.filter(name=tag):
                    Tags.objects.create(name=tag)
                article.tags.add(Tags.objects.get(name=tag))
            article.check()
            article.save()

        self.stdout.write('Successfully insert blog data')
