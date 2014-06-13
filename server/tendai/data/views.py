from django.http import HttpResponse
from django.db.models import Count
from openrosa import models as or_models
import json
from datetime import datetime
from collections import defaultdict
import csv
from StringIO import StringIO

def submissions_per_day(request, country_code):
    output = StringIO()
    writer = csv.writer(output)
    counts = defaultdict(int, {})
    submissions = or_models.ORFormSubmission.objects.all().filter(submissionworkerdevice__community_worker__country__code=country_code)
    for submission in submissions:
        if submission.end_time:
            date = datetime.strftime(submission.end_time,"%Y-%m-%d")
            counts[date] += 1
    writer.writerow(["Date", "Count"])
    for key in sorted(counts.keys()):
        writer.writerow([key, counts[key]])
    output.seek(0)
    
    return HttpResponse(output.read())
    
