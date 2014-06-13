from __future__ import division
import csv
from collections import defaultdict
import sys

from django.core.management.base import BaseCommand, CommandError

from devices.models import SubmissionWorkerDevice

class Command(BaseCommand):
    def handle(self, *args, **options):
        writer = csv.writer(sys.stdout)
        writer.writerow(["Year", "Month", "Country", "% Valid", "Number Submissions"])

        valid_register = defaultdict(list)
        for swd in SubmissionWorkerDevice.objects.all():
            date = swd.created_date
            if swd.community_worker and swd.community_worker.country:
                key = (date.year, date.month, swd.community_worker.country.name)
                if swd.verified:
                    valid_register[key].append(swd.valid)
        for (year, month, country), register in valid_register.items():
            if len(register):
                perc = len([x for x in register if x]) / len(register)
                writer.writerow([str(year), str(month), country, perc, len(register)])
