# A2WSGI

This example is to demonstrate support for [`a2wsgi`](https://github.com/abersheeran/a2wsgi), available since BlackSheep `2.6.1`.

1. Create a virtual environment and activate it.
1. Install dependencies.
1. Run with the command below.

## Testing with Gunicorn

```python
pip install blacksheep a2wsgi gunicorn

gunicorn server:wsgi_app -w 4
```

## Testing with uWSGI

```python
pip install uwsgi

uwsgi --http :8000 --wsgi-file server.py --callable wsgi_app
```
