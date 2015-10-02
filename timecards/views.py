import csv
import logging
import traceback
from datetime import date, timedelta

from django.conf import settings
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render

from timecards import models

from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook


logger = logging.getLogger(__name__)

writer_name = getattr(settings, 'WRITER', 'csv')

if writer_name == 'csv':

    class Writer(object):
        content_type = 'text/csv'
        extension='csv'
        def __init__(self, buf):
            self.writer = csv.writer(buf)

        def writerow(self, row):
            self.writer.writerow(row)

        def close(self):
            None

if writer_name == 'excel':

    class Writer(object):
        content_type = \
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        extension = 'xlsx'
        def __init__(self, buf):
            self.buffer = buf
            self.workbook = Workbook()
            self.worksheet = self.workbook.active

        def writerow(self, row):
            self.worksheet.append(row)

        def close(self):
            self.buffer.write(save_virtual_workbook(self.workbook))


months = [
    'None', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep',
    'Oct', 'Nov', 'Dec']

def week_name(week):
    return '%s %s-%s' % (months[week[0].month], week[0].day, week[1].day)

def last_month_report_view(request):

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = ('attachment; filename=hours.{0}'
        .format(Writer.extension))

    writer = Writer(response)

    today = date.today()
    one_month_ago = models.subtract_from_date(today, months=1)
    last_month_first = date(one_month_ago.year, one_month_ago.month, 1)
    last_month_end = models.subtract_from_date(
        date(today.year, today.month, 1), days=1)
    weeks = [ [
        last_month_first,
        last_month_first + timedelta(days=(6 - last_month_first.weekday()))] ]
    for i in range(1, 5):
        weeks.append( [
            weeks[i-1][1] + timedelta(days=1),
            weeks[i-1][1] + timedelta(days=7)] )
    weeks[4][1] = last_month_end
    if weeks[4][0] > last_month_end:
        weeks.pop()

    write_week_headers(writer, weeks)

    write_week_rows(writer, weeks)
    return response


def write_week_headers(writer, weeks):
    writer.writerow([
        'Product', 'Component', 'Bug', 'Summary'] + [ week_name(week)
        for week in weeks ])

def write_week_rows(writer, weeks):
    rows = []
    for week in weeks:
        rows += get_rows_for_week(week, weeks)

    for i, row in enumerate(rows):
        writer.writerow(row)

    writer.writerow(['', '', '', '',]  + [
        '=sum({0}2:{0}{1})'.format('EFGHIJ'[n], i+2)
        for n, w in enumerate(weeks) ] + [
        '=sum(E{0}:{1}{0})'.format(i+3, 'EFGHIJ'[len(weeks)-1]) ])
    writer.close()

def get_rows_for_week(week, weeks):
    start, end = week
    bugs = (models.TimeCard.objects
        .filter(date__gte=start, date__lte=end)
        .exclude(bug=None)
        .values('bug')
        .annotate(Count('id')).order_by('bug'))
    week_rows = []
    for bug in ([
            models.get_bug(item['bug'])['bugs'][0] for item in bugs ] +
            [ {
                'id': None,
                'product': '',
                'component': '',
                'summary': 'Overhead'} ]):
        cards = models.TimeCard.objects.filter(
            date__gte=start, date__lte=end, bug=bug['id'])
        hours = sum([ card.hours for card in cards ])
        week_rows.append(
            [
                bug['product'].encode('utf-8'),
                bug['component'].encode('utf-8'),
                bug['id'], bug['summary'].encode('utf-8') ] +
            [
                (hours if week == weeks[i] else '')
                for i, w in enumerate(weeks) ])
    week_rows.sort()
    return week_rows

def update_bug_info_view(request):
    """Update the bug info on every card"""
    response = HttpResponse()
    for card in models.TimeCard.objects.exclude(bug=None):
        try:
            card.update_bug_info()
        except:
            logger.error(traceback.format_exc())
    return HttpResponse(status=204)
