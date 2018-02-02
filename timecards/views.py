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

def this_week_report_view(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = ('attachment; filename=hours.{0}'
        .format(Writer.extension))

    writer = Writer(response)

    today = date.today()
    first_of_week = today - timedelta(days=today.weekday() + 2)
    weeks = [ [first_of_week, today] ]

    write_week_headers(writer, weeks)

    write_week_rows(writer, weeks)
    return response

def timesheet_report(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = ('attachment; filename=hours.{0}'
        .format(Writer.extension))

    writer = Writer(response)

    today = date.today()
    first_of_week = today - timedelta(days=today.weekday() + 3)

    writer.writerow([
        '', '', '', '', '', 'Weekly time report'])
    writer.writerow(['', 'P. Scott DeVos'])
    writer.writerow([])
    writer.writerow([
        '',
        'Employee:',
        'P. Scott DeVos',
        '',
        'Employee phone:',
        '414-698-7047'])
    writer.writerow([
        '',
        'Manager:',
        'David Barrios',
        '',
        'Employee email:',
        'scott.devos@sykes.com'])
    writer.writerow([])
    writer.writerow(['', today.strftime('%D')])
    writer.writerow([])
    writer.writerow([
        '',
        'Day',
        '',
        'Project OneSykes',
        'Non-Project Meetings',
        'Non-Project Tasks / PTO',
        'Travel',
        'Total'])

    day = first_of_week
    row = 10
    while day <= today:
        writer.writerow(
            [''] + get_row_for_day(day) + ['=sum(D{0}:G{0})'.format(row) ])
        day += timedelta(days=1)
        row += 1
    writer.writerow(['', '', 'Total hours'] + [
        '=sum({0}10:{0}16)'.format(col) for col in 'DEFGH'])
    writer.writerow(['', '', 'Rate per hour'])
    writer.writerow(['', '', 'Total pay'])
    writer.writerow([])
    writer.writerow(
        ['', '', '', 'P. Scott DeVos', '', '', '', today.strftime('%D')])
    writer.writerow(['', '', '', 'Employee signature', '', '', '', 'Date'])
    writer.writerow([])
    writer.writerow(['', '', '', 'Manager signature', '', '', '', 'Date'])
    writer.close()
    return response

def this_month_report_view(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = ('attachment; filename=hours.{0}'
        .format(Writer.extension))

    writer = Writer(response)

    today = date.today()
    first_of_month = date(today.year, today.month, 1)
    weeks = [ [
        first_of_month,
        first_of_month + timedelta(days=(6 - first_of_month.weekday()))] ]
    for i in range(1, 5):
        weeks.append( [
            weeks[i-1][1] + timedelta(days=1),
            weeks[i-1][1] + timedelta(days=7)] )
    weeks[4][1] = today
    while weeks[-1][0] > today:
        weeks.pop()

    write_week_headers(writer, weeks)

    write_week_rows(writer, weeks)
    return response



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

def parse_time_card(time_card, project, meeting, tasks, travel, with_bug):
    description = time_card.description.lower()
    hours = time_card.hours
    if with_bug and 'non project' in description:
        tasks += hours
    elif not with_bug and 'non project' in description:
        meeting += hours
    elif 'onesykes' in description:
        project += hours
    elif 'meeting' in description or 'stand' in description:
        if with_bug:
            project += hours
        else:
            meeting += hours
    elif 'travel' in description:
        travel += hours
    else:
        tasks += hours
    return project, meeting, tasks, travel

def get_row_for_day(day):
    time_cards = models.TimeCard.objects.filter(date=day)
    print day.strftime('%D'), time_cards.count(), sum([ tc.hours for tc in time_cards])
    project = 0.0
    meeting = 0.0
    tasks = 0.0
    travel = 0.0
    for time_card in time_cards:
        if time_card.bug is None:
            project, meeting, tasks, travel = parse_time_card(
                time_card, project, meeting, tasks, travel, False)
        else:
            #try:
            bug_data = models.get_bug(time_card.bug)
            #except:
            #    print("Could not get bug {0}".format(time_card.bug))
            #    bug_data = None
            if bug_data and bug_data.get('bugs'):
                bug = bug_data['bugs'][0]
                if ((
                            bug['product'] == 'DARI' or
                            bug['product'] == 'Maestro' or
                            bug['product'] == 'porpoiseflow') and
                        bug['severity'] == 'enhancement'):
                    project += time_card.hours
                else:
                    tasks += time_card.hours
            else:
                project, meeting, tasks, travel = parse_time_card(
                    time_card, project, meeting, tasks, travel, True)
    project = project or ''
    meeting = meeting or ''
    tasks = tasks or ''
    travel = travel or ''
    return [
        day.strftime('%A'), day.strftime('%D'), project, meeting, tasks, travel
    ]

def get_rows_for_week(week, weeks):
    start, end = week
    bugs = (models.TimeCard.objects
        .filter(date__gte=start, date__lte=end)
        .exclude(bug=None)
        .values('bug')
        .annotate(Count('id')).order_by('bug'))
    week_rows = []
    try:
       [ models.get_bug(item['bug'])['bugs'][0] for item in bugs ]
    except:
        import ipdb; ipdb.set_trace()
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
