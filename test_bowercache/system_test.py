"""System tests for Bower Cache."""
from __future__ import print_function
import subprocess
import time

import requests

def test_on_demand_caching(tmpdir):
    """A system test for on-demand caching.

    Set up a site. Run Gunicorn, a single Celery worker and a git daemon.

    Do a request against the cache for a Bower library. Keep performing
    requests until the library has been cached.
    """
    tmp_path = str(tmpdir)
    package_name = 'html5-boilerplate'

    print("Creating site in " + tmp_path + " ...")
    subprocess.check_call("bower-cache-init " + tmp_path, shell=True)
    print("Site created.")
    print("Starting Gunicorn...")
    gunicorn = subprocess.Popen(['gunicorn', 'bowercachesite.wsgi:application'],
                                cwd=tmp_path)
    time.sleep(5)
    print("Gunicorn started.")
    print("Starting a single Celery worker...")
    celery = subprocess.Popen(['./manage.py', 'celery', 'worker', '-c 1', '-B'],
                                cwd=tmp_path)
    time.sleep(5)
    print("Celery started.")

    print("Firing off request for package {0}".format(package_name))
    url = 'http://localhost:8000/packages/{0}'.format(package_name)

    resp = requests.get(url)

    print("Waiting for the worker to clone it...")
    time.sleep(10)

    assert tmpdir.join('cache', package_name).check()

    gunicorn.terminate()
    gunicorn.wait()

    celery.terminate()
    celery.wait()

    time.sleep(2)
    print("All done.")
