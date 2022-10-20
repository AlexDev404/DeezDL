import os
import requests
from urllib.parse import urlparse


def download(url, path, optname):
    url = str(url)
    if not path:
        path = os.getcwd()
    else:
        path = os.path.join(path)
    g = requests.get(url, allow_redirects=True)
    url = urlparse(url)
    os.makedirs(path, exist_ok=True)
    name = ""
    if not optname:
        name = os.path.basename(url.path)
    else:
        filename, file_extension = os.path.splitext(os.path.basename(url.path))
        name = optname + file_extension
    path = os.path.join(path, name)
    open(path, 'wb').write(g.content)
