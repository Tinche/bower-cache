"""Functionality for the bower-cache init command."""
from __future__ import print_function

import os
import sys

from pkg_resources import resource_filename

from django.core import management

import bowercache


def init_site():
    """Initialize a Bower Cache site using the template."""
    site_name = 'bowercachesite'
    dir_name = sys.argv[1] if len(sys.argv) > 1 else site_name
    settings = site_name + ".settings"
    template_filename = resource_filename(bowercache.__name__,
                                          'project_template')
    cwd = os.getcwd()
    full_dir_name = os.path.join(cwd, dir_name)

    startproject_args = ['startproject', site_name]
    if dir_name != site_name:
        startproject_args.append(dir_name)

    management.call_command(*startproject_args, template=template_filename)

    # Now magically turn into manage.py!
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings)
    if not dir_name == '.':
        sys.path.insert(0, full_dir_name)

    from django import conf
    reload(conf)
    reload(management)

    management.call_command('collectstatic', interactive=False)
    management.call_command('syncdb', interactive=False)
    management.call_command('createsuperuser', username='admin',
                            email='root@localhost', interactive=False)

    os.mkdir(conf.settings.REPO_ROOT)