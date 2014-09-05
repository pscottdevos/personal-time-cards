from datetime import date, datetime, time, timedelta
from django.conf import settings
from django.core import exceptions
from django.db import models
from django.db.models import Q

# Create your models here.

def subtract_from_date(dt, months=0, weeks=0, days=0):

    assert months >= 0
    assert weeks >= 0
    assert days >= 0
    if months:
        def days_in_prior_month(dt, months):
            # the day of the month of the day prior to the first day of THIS month
            # is the number of days in LAST month
            last_day_of_last_month = dt - timedelta(days=dt.day)
            if months == 1:
                return last_day_of_last_month.day    
            else:
                return (
                    last_day_of_last_month.day +
                    days_in_prior_month(last_day_of_last_month, months-1)
                )
        days += days_in_prior_month(dt, months)
    return dt - timedelta(days=days, weeks=weeks)


class TimeCard(models.Model):
    """Time Card Entries"""

    bug = models.IntegerField(blank=True)
    date = models.DateField(blank=False)
    start = models.TimeField(blank=True, unique_for_date='date')
    end = models.TimeField(blank=False, unique_for_date='date')
    description = models.TextField(blank=True)


    @property
    def hours(self):
        return round(
            (datetime.combine(self.date, self.end) - datetime.combine(self.date, self.start)).seconds/3600.0, 2)

    @property
    def short_description(self):
        return self.description.split('\n')[0]

    def clean(self):
        priors = self.priors()
        if not self.start:
            if not priors:
                raise exceptions.ValidationError(
                    'You must provide a start date for the first time card '
                    'of the day'
                )
            else:
                start = priors.aggregate(end=models.Max('end'))['end']
        else:
            start = self.start

        if self.end and self.end < start:
            raise exceptions.ValidationError(
                'End date must be greater than start date'
            )

    @property
    def url(self):
        return '{0}/show_bug.cgi?id={1}'.format(settings.BUGZILLA_ROOT, self.bug)

    def anchor(self):
        return '<a href="{0}">{1}</a>'.format(self.url, self.bug)


    def save(self):
        if not self.start:
            priors = self.priors()
            if priors:
                end = priors.aggregate(end=models.Max('end'))['end']
            self.start = end
        super(TimeCard, self).save()

    def priors(self):
        """Returns a list queryset of time cards for the current date"""
        return TimeCard.objects.filter(date=self.date)

        

    def __unicode__(self):
        return '%s: %s-%s' % (self.date, self.start, self.end)
