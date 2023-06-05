# blog



firstStart

```
pip3 install -r requirements.txt
pip3 install gunicorn
pip3 install gunicorn[eventlet]
# edit my_blog/settings.py
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic
```

