#!/usr/bin/env python

from django.core.management import setup_environ
import settings

setup_environ(settings)

from datetime import date
import devices.models

START_YEAR = 2011
START_MONTH = 10

MONTH = (None, 'jan', 'feb', 'mar', 'apr', 'may', 'jun',
         'jul', 'aug', 'sep', 'oct', 'nov', 'dec')

def get_months():
    today = date.today()
    months = []
    for year in range(START_YEAR, today.year+1):
        if year == START_YEAR: m = range(START_MONTH, 13)
        elif year == today.year: m = range(1, today.month+1)
        else: m = range(1, 13)
        for month in m:
            months.append((year, month))
    return months

def get_monitor_district(monitor):
     swd = devices.models.SubmissionWorkerDevice.objects.all_valid.all()
     swd = swd.filter(community_worker=monitor)
     swd = swd.filter(submission__form__name='Facility Form')
     d = [s.submission.content.section_name.facility_district for s in swd if s.submission.form.name == "Facility Form"]
     districts = set(d)
     if len(districts) == 0:
         return 'Unknown'
     if len(districts) == 1:
         return districts.pop()
     return ' or '.join(districts)

def dump_monitor_stats():
    data = []
    data.append('monitor name')
    data.append('organisation')
    for month in get_months():
        data.append('%s %4d' % (MONTH[month[1]], month[0]))
    data.append('district')
    data.append('letter of authority received')
    data.append('any issues preventing data collection')
    data.append('resolutions to correct these problems')
    print ','.join(data)
    for monitor in devices.models.CommunityWorker.objects.all_active.all():
        submissions = devices.models.SubmissionWorkerDevice.objects.all_valid.filter(community_worker=monitor)
        data = []
        data.append('%s %s' % (monitor.first_name, monitor.last_name))
        data.append('%s' % (monitor.organisation))
        for month in get_months():
            s = submissions.filter(created_date__year=month[0], created_date__month=month[1])
            data.append('%d' % (s.count()))
        data.append(get_monitor_district(monitor))
        data.append('')
        data.append('')
        data.append('')
        print ','.join(data)
    return

if __name__ == '__main__':
    dump_monitor_stats()
