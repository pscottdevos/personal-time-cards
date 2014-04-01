from datetime import date, datetime, time
from django.core import exceptions
from django.db import models

# Create your models here.


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



class TcCode(models.Model):
    """Codes to bill against"""

    STATUS_CHOICES = (
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

    def monthly_hours_to_date(self):
        m1 = date(date.today().year, date.today().month, 1)
        cards = TimeCard.objects.filter(code=self, date__gte=m1, date__lte=date.today())
        return round(sum([c.hours for c in cards]), 2)

    def __unicode__(self):
        return '%s: %s%s' % (self.project.name, self.code, ' - %s' % (self.description) if self.description else '')


class TimeCard(models.Model):
    """Time Card Entries"""

    code = models.ForeignKey('TcCode')
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
    def monthly_hours_for_code_to_date(self):
        m1 = date(self.date.year, self.date.month, 1)
        cards = TimeCard.objects.filter(code=self.code, date__gte=m1, date__lte=self.date)
        return round(sum([c.hours for c in cards]), 2)

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
