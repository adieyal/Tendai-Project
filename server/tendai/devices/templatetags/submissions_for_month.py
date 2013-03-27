from django import template
import datetime

register = template.Library()

@register.filter
def submissions_for_month(submissions, mydate):
    """
    expect submissions_for_month|"month,year"
    """
    month, year = mydate.split(",")
    #month, year = mydate.month, mydate.year
    month, year = int(month), int(year)


    return submissions.filter(created_date__year=year, created_date__month=month)
