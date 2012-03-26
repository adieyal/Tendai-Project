from os import path
from django.conf import settings
from django.http import HttpResponse, Http404
from django.shortcuts import redirect, get_object_or_404

from fuzzywuzzy import fuzz
from datetime import datetime, timedelta
from django.db.models import Count

import devices.models as dev_models
import openrosa.models as or_models
from scorecard import ScoreCardGenerator, Month


def index(request):
    return Http404

def scorecard(request, country, year=2011, month=12):
    year, month = int(year), int(month)
    month = Month(int(year), int(month))
    country = get_object_or_404(dev_models.Country, code=country)
    template = open(path.join(settings.STATIC_ROOT, 'scorecard.svg'))

    scorecard_generator = ScoreCardGenerator(template, settings.STATIC_ROOT)
    svg = scorecard_generator.render_all(country, month)

    response = HttpResponse(svg, mimetype='image/svg+xml')
    filename = 'scorecard_%s.svg' % (country.code.lower())
    response['Content-Disposition'] = 'filename=%s' % (filename)
    return response
