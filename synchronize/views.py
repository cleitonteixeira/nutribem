from django.shortcuts import render

import logging

logger = logging.getLogger(__name__)

from django.http import HttpResponse


def synchronize(request):
    return HttpResponse(content="Sincronizado", status=200)