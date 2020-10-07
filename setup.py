import os

from setuptools import setup

setup(
    name='life_scheduler',
    license='BSD-3',
    author='Bartlomiej Puget',
    author_email='larhard@gmail.com',
    setup_requires=['libsass >= 0.6.0'],
    sass_manifests={
        'life_scheduler': {
            'sass_path': '../static/sass',
            'css_path': '../static/css',
            'wsgi_path': '/static/css',
            'strip_extension': True,
        },
    }
)
