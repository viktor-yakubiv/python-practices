import logging
from django.conf import settings
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import render

import os

logger = logging.getLogger(__name__)


def index(request, path):
    abspath = os.path.join(settings.INDEX, path)
    if not os.path.exists(abspath):
        logger.error("Path does not exists: %s" % abspath)
        raise Http404("Path does not exists")
    if os.path.isfile(abspath):
        return send_file(request, abspath)
    if os.path.isdir(abspath):
        return list_directory(request, abspath)


def list_directory(request, abspath):
    files = os.listdir(abspath)
    files_verbose = []
    for file in files:
        file_path = os.path.join(abspath, file)
        files_verbose.append({
            'name': file,
            'url': './' + file + ('/' if os.path.isdir(file_path) else ''),

            'isdir': os.path.isdir(file_path),
            'isfile': os.path.isfile(file_path),
            'islink': os.path.islink(file_path),
        })
    context = {
        'current': request.path,
        'root': abspath == settings.INDEX,
        'files': files_verbose,
    }
    logger.info("Access to %s" % abspath)
    return render(request, 'index.html', context)


def send_file(request, abspath):
    logger.info('Downloading: %s' % abspath)
    with open(abspath, 'rb') as fh:
        response = HttpResponse(fh.read(), content_type="application/octet-stream")
        response['Content-Disposition'] = 'inline; filename=' + os.path.basename(abspath)
        response['Content-Length'] = os.path.getsize(abspath)
        return response
