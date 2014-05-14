## Bower Cache (the Python/Django edition)

[![Build Status](https://travis-ci.org/Tinche/bower-cache.png)](https://travis-ci.org/Tinche/bower-cache)
[![Coverage Status](https://coveralls.io/repos/Tinche/bower-cache/badge.png?branch=master)](https://coveralls.io/r/Tinche/bower-cache?branch=master)
[![Requirements Status](https://requires.io/github/Tinche/bower-cache/requirements.png?branch=master)](https://requires.io/github/Tinche/bower-cache/requirements/?branch=master)

This is a combination Bower registry/caching proxy. It can do two things:

* act as a registry (a name to URL mapper) for remote packages.
* act as a caching proxy for remote Bower packages.

The admin interface is available for both functionalities.

## Install

We strongly suggest installing into a virtualenv.

    virtualenv .
    . bin/activate
    pip install bower-cache

## Create a site

After Bower Cache has been installed, use the bower-cache-init command to
initialize a Bower Cache site. The site contains configuration and is where the
packages are actually cached.

    bower-cache-init /var/lib/bower-cache

The site contains a standard Django manage.py file. In order to log into the
admin site, the admin user (which has been created as part of site
initialization) needs a password. Set it by running

    python manage.py changepassword admin

## Run the services

Bower Cache requires several services to run for it to be fully functional. The
commands listed expect to be run from the site directory (the directory
containing manage.py).

Run Gunicorn to serve the REST interface and admin site:

    gunicorn bowercachesite:wsgi

Run a single-process Celery worker, including the scheduler (-B):

    python manage.py celery worker -c 1 -B

Run a git daemon to serve the cached packages:

    git daemon --export-all --base-path=<site>/cache

## Admin interface

If you're using the dev server, the admin will be available at 
http://127.0.0.1:8000/admin by default. Open the URL and log in as the admin.

The admin interface allows managing the cached packages, including manually
issuing caching tasks and setting up daily package updates.

## License

Copyright © 2013 Toran Billups, Tin Tvrtković.

Licensed under the MIT License
