import csv
import logging
import traceback
from datetime import date, timedelta
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render
from timecards import models


logger = logging.getLogger(__name__)

# Create your views here.

months = ['None', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
def week_name(week):
    return '%s %s-%s' % (months[week[0].month], week[0].day, week[1].day)

def last_month_report_view(request):

    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=hours.csv'

    writer = csv.writer(response)

    today = date.today()
    one_month_ago = models.subtract_from_date(today, months=1)
    last_month_first = date(one_month_ago.year, one_month_ago.month, 1)
    last_month_end = models.subtract_from_date(date(today.year, today.month, 1), days=1)
    weeks = [ [last_month_first, last_month_first + timedelta(days=(6 - last_month_first.weekday()))] ]
    for i in range(1, 5):
        weeks.append( [weeks[i-1][1] + timedelta(days=1), weeks[i-1][1] + timedelta(days=7)] )
    weeks[4][1] = last_month_end
    if weeks[4][0] > last_month_end:
        weeks.pop()
    
    writer.writerow(['Product', 'Component', 'Bug', 'Summary'] + [ week_name(week) for week in weeks ])
    rows = []
    for week in weeks:
        bugs = models.TimeCard.objects.filter(date__gte=week[0], date__lte=week[1]).exclude(bug=None
        ).values('bug').annotate(Count('id')).order_by('bug')
        week_rows = []
        for bug in [ models.get_bug(item['bug'])['bugs'][0] for item in bugs ]:
            cards = models.TimeCard.objects.filter(date__gte=week[0], date__lte=week[1], bug=bug['id'])
            hours = sum([ card.hours for card in cards ])
            week_rows.append(
                [ bug['product'].encode('utf-8'), bug['component'].encode('utf-8'),
                  bug['id'], bug['summary'].encode('utf-8') ] +
                [ (hours if week == weeks[i] else '') for i, w in enumerate(weeks) ])
        week_rows.sort()
        rows += week_rows
    for row in rows:
        print row[3], type(row[3])
        writer.writerow(row)
    #[ writer.writerow(row) for row in rows ]
    return response


def update_bug_info_view(request):
    """Update the bug info on every card"""
    response = HttpResponse()
    for card in models.TimeCard.objects.exclude(bug=None):
        try:
            card.update_bug_info()
        except:
            logger.error(traceback.format_exc())
    return HttpResponse(status=204)
