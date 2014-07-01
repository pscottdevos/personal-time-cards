from datetime import date, datetime, time, timedelta
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


class TcProject(models.Model):
    """Projects to bill against"""

    STATUS_CHOICES = (
        ('PROPOSED', 'Proposed'),
        ('ACTIVE', 'Active'),
        ('CLOSED', 'Closed'),
    )

    name = models.CharField(max_length=50, unique=True, blank=False)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, blank=False
    )

    def __unicode__(self):
        return self.name

    def _hours_in_week_last_month(self, week):
        today = date.today()
        m1 = subtract_from_date(today, months=1)
        m1 = date(m1.year, m1.month, 1)
        m2 = today - timedelta(today.day)
        wstart = m1 + timedelta(weeks=(week - 1))
        wstart = wstart if wstart < m2 else m2
        wend = wstart + timedelta(days=6)
        wend = wend if wend < m2 else m2
        cards = TimeCard.objects.filter(code__project=self, date__gte=wstart, date__lte=wend)
        return round(sum([c.hours for c in cards]), 2)

    def hours_in_week_1_last_month(self):
        return self._hours_in_week_last_month(1)

    def hours_in_week_2_last_month(self):
        return self._hours_in_week_last_month(2)

    def hours_in_week_3_last_month(self):
        return self._hours_in_week_last_month(3)

    def hours_in_week_4_last_month(self):
        return self._hours_in_week_last_month(4)

    def hours_in_week_5_last_month(self):
        return self._hours_in_week_last_month(5)


class TcCode(models.Model):
    """Codes to bill against"""

    STATUS_CHOICES = (
        ('OVERHEAD', 'Overhead'),
        ('PROPOSED', 'Proposed'),
        ('PRE', 'Pre-production'),
        ('POST', 'Post-production'),
        ('CLOSED', 'Closed'),
    )

    code = models.CharField(max_length=10, blank=False)
    description = models.CharField(max_length=255, blank=True)
    project = models.ForeignKey('TcProject', blank=False)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, blank=False
    )

    @property
    def hours_last_month(self):
        today = date.today()
        m1 = subtract_from_date(today, months=1)
        m1 = date(m1.year, m1.month, 1)
        m2 = today - timedelta(today.day)
        cards = TimeCard.objects.filter(code=self, date__gte=m1, date__lte=m2)
        return round(sum([c.hours for c in cards]), 2)

    @property
    def hours_last_week(self):
        today = date.today()
        w2 = today - timedelta(today.weekday()) - timedelta(days=2) # Monday.weekday() = 0 so EOW will be Saturday
        w1 = w2 - timedelta(days=6)
        print w1, w2
        cards = TimeCard.objects.filter(code=self, date__gte=w1, date__lte=w2)
        return round(sum([c.hours for c in cards]), 2)

    def __unicode__(self):
        return '%s: %s%s' % (self.project.name, self.code, ' - %s' % (self.description) if self.description else '')


class TimeCard(models.Model):
    """Time Card Entries"""

    code = models.ForeignKey('TcCode', limit_choices_to=~Q(project__status='CLOSED'))
    date = models.DateField(blank=False)
    start = models.TimeField(blank=True, unique_for_date='date')
    end = models.TimeField(blank=False, unique_for_date='date')
    description = models.TextField(blank=True)

    @property
    def hours(self):
        return round(
            (datetime.combine(self.date, self.end) - datetime.combine(self.date, self.start)).seconds/3600.0,
        2)

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
