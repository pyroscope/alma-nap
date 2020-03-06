# -*- coding: utf-8 -*-
"""Automated tasks."""
from __future__ import unicode_literals

import os
import sys
import subprocess

from invoke import task

ROOTDIR = os.path.dirname(__file__)
PROJECT = os.path.basename(ROOTDIR)
BINDIR = "{}/.venv/bin/".format(ROOTDIR)
RUN_PLAYBOOK = "{bin}ansible-playbook -i hosts -l {prj}-{env} site.yml{opt}"


@task
def _bootstrap(ctx):
    """Internal, called by 'bootstrap.sh'."""
    cache_dir = os.path.join(ROOTDIR, '.cache')
    if not os.path.isdir(cache_dir):
        os.makedirs(cache_dir)


@task(help=dict(dir="Run in given directory"))
def readme(ctx, dir='.'):
    """Preview and auto-reload the README locally."""
    subprocess.call(BINDIR + "grip --title='README for “{}”' -b README.rst".format(PROJECT), shell=True, cwd=dir)


@task(help=dict(tags="Set Ansible tags"))
def setup_dev(ctx, tags=''):
    """Set up development server."""
    if tags:
        tags = ' -t ' + tags
    ctx.run(RUN_PLAYBOOK.format(bin=BINDIR, prj=PROJECT, opt=tags, env='dev'))


@task(help=dict(tags="Set Ansible tags"))
def setup_prod(ctx, tags=''):
    """Set up production server."""
    if tags:
        tags = ' -t ' + tags
    ctx.run(RUN_PLAYBOOK.format(bin=BINDIR, prj=PROJECT, opt=tags, env='prod'))
