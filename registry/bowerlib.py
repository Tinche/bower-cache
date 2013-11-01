"""Bower utilities."""
import requests


def get_package(repo_url, pkg_name, timeout=1):
    """Retrieve package information from a Bower registry at repo_url.

       Returns a dict of package data."""
    url = repo_url + "/packages/" + pkg_name
    headers = {'accept': 'application/json'}
    resp = requests.get(url, headers=headers, timeout=timeout)
    if resp.status_code == 404:
        return None
    return resp.json()
