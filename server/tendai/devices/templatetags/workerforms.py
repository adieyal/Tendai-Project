from django import template
import datetime

register = template.Library()

@register.filter
def workerforms(worker, form=None):
    if form:
        submissions =  worker.my_submissions.filter(submission__form__name=form)
    else:
        submissions = worker.my_submissions

    return submissions

@register.filter
def previous_month_submissions(submissions):
    timeargs = {
        "day" : 1,
        "hour" : 0,
        "minute" : 0,
        "second" : 0,
        "microsecond" : 0,
    }

    start_of_month = datetime.datetime.utcnow().replace(**timeargs)
    end_of_prev_month = start_of_month - datetime.timedelta(seconds=1)
    start_of_prev_month = end_of_prev_month.replace(**timeargs)

    return submissions.filter(created_date__gte=start_of_prev_month, created_date__lte=end_of_prev_month)

