import csv
import sys

from django.core.management.base import BaseCommand, CommandError

from devices.models import Medicine
from general.utils import Month

class Command(BaseCommand):
    def handle(self, *args, **options):
        writer = csv.writer(sys.stdout)
        writer.writerow(["Year", "Month", "Medicine", "Country", "Stockout Days"])

        for year in [2012, 2013, 2014]:
            for month in range(1, 13):
                for medicine in Medicine.objects.all():
                    for country in medicine.countries.all():
                        m = Month(year, month)
                        stockout_days = medicine.stockout_days(country, m)
                        writer.writerow([str(year), str(month), str(medicine), str(country), stockout_days])


