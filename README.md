## Bower Cache (the Python/Django edition)

[![Build Status](https://travis-ci.org/Tinche/bower-cache.png)](https://travis-ci.org/Tinche/bower-cache)
[![Coverage Status](https://coveralls.io/repos/Tinche/bower-cache/badge.png?branch=master)](https://coveralls.io/r/Tinche/bower-cache?branch=master)

This is a combination Bower registry/caching proxy. It can do two things:

* act as a registry (a name to URL mapper) for remote packages.
* act as a caching proxy for remote Bower packages.

The admin interface is available for both functionalities.

## Install the dependencies

    mkvirtualenv registry
    pip install -r requirements.txt

## Sync your database and create an admin user

    python manage.py syncdb

## Run the webserver locally

    python manage.py runserver

## Log into the admin

If you're using the dev server, the admin will be available at 
http://127.0.0.1:8000/ by default. Open the URL and log in as the admin.

## Clone and cache remote Bower repositories

Ensure the correct values are set in the settings (registry/settings.py).

REPO_ROOT is the local file system path to a writable directory into which the
remote repositories will be cloned.

REPO_URL is the URL fragment the system will prepend to the repository names
to create the repository URL.

It is generally expected a git daemon will be run separately and will serve
the REPO_ROOT directory:

git daemon --export-all --base-path=/var/git/

After this is set up, remote repositories can be cloned from the admin via the
'Add Cloned Repo' button. For example, creating a cloned repo with the name
'jquery' and origin 'https://github.com/jquery/jquery.git' will check out 
jQuery into the REPO_ROOT directory, and map the name 'jquery' to REPO_URL + 
'jquery'.

## Development

    python manage.py test test
      
## License

Copyright © 2013 Toran Billups, Tin Tvrtković.

Licensed under the MIT License
