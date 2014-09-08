import json
import logging
import requests

from datetime import date, datetime, time, timedelta
from django.conf import settings
from django.core import exceptions
from django.db import models
from django.db.models import Q

logger = logging.getLogger(__name__)

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

    bug = models.IntegerField(blank=True, null=True)
    bug_summary = models.CharField(max_length=255, blank=True)
    add_to_bug_comments = models.BooleanField(default=False)
    bug_comment_added = models.BooleanField(default=False)
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

    @property
    def url(self):
        return '{0}/show_bug.cgi?id={1}'.format(settings.BUGZILLA_ROOT, self.bug)

    def bug_get(self, rpc_method, params=None):
        url = '{0}/jsonrpc.cgi'.format(settings.BUGZILLA_ROOT)
        data = {
            'method': 'Bug.' + rpc_method,
            'params': json.dumps([ {
                'ids': [self.bug],
                'Bugzilla_login': settings.BUGZILLA_USERNAME,
                'Bugzilla_password': settings.BUGZILLA_PASSWORD,
            } ]),
        }
        response = requests.get(url=url, params=data, verify=False)
        return json.loads(response.text)['result']

    def bug_post(self, rpc_method, params):
        url = '{0}/jsonrpc.cgi'.format(settings.BUGZILLA_ROOT)
        headers = {'content-type': 'application/json-rpc'}
        data = json.dumps({
            'method': 'Bug.' + rpc_method,
            'id': self.id,
            'params': [ {
                'id': self.bug,
                'comment': self.description,
                'Bugzilla_login': settings.BUGZILLA_USERNAME,
                'Bugzilla_password': settings.BUGZILLA_PASSWORD,
            } ],
        })
        return requests.post(url=url, headers=headers, data=data, verify=False)

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

    def get_anchor(self):
        return '<a href="{0}">{1}</a>'.format(self.url, self.bug)

    def get_bug_info(self):
        return self.bug_get('get')['bugs'][0]

    def post_bug_comment(self, comment):
        params = {
            'id': self.bug,
            'comment': comment,
        }
        return self.bug_post('add_comment', params).status_code


    def priors(self):
        """Returns a list queryset of time cards for the current date"""
        return TimeCard.objects.filter(date=self.date)

    NO_BUG_SUMMARY = "<bug summary not available at this time>"

    def save(self):
        if not self.start:
            priors = self.priors()
            if priors:
                end = priors.aggregate(end=models.Max('end'))['end']
            self.start = end

        if self.bug:
            if not self.bug_summary or self.bug_summary == self.NO_BUG_SUMMARY:
                try:
                    self.bug_summary = self.get_bug_info()['summary'][:255]
                except Exception:
                    import traceback
                    logger.error(traceback.format_exc())
                    self.bug_summary = self.NO_BUG_SUMMARY
            if self.bug_comment_added:
                self.add_to_bug_comments = True
            elif self.add_to_bug_comments and self.description.strip():
                self.bug_comment_added = self.post_bug_comment(self.description.strip()) == 200 

        super(TimeCard, self).save()

    def __unicode__(self):
        return '%s: %s-%s' % (self.date, self.start, self.end)
