# coding=utf-8
import json
import pytils
from apps.programms.models import ProgramItem
from apps.tv.managers import get_local_time, time_kanal_match, DEFAULT_TZ
from apps.tv.utils import CurrentTVWeekDates
from annoying.decorators import ajax_request
from apps.tv.models import TVProgram, TVProgramItem
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.csrf import csrf_exempt
from apps.tv.parser import TVCSVParser
from django.views.generic import TemplateView
from datetime import datetime, timedelta
from django.http import HttpResponse
from datetime import timedelta
from django.http import JsonResponse
from django.core import serializers
import json
from django.views.generic.base import View
from rest_framework.mixins import ListModelMixin
from rest_framework.generics import GenericAPIView
from apps.tv.serializer import TVSERIALIZER



class TvPage(TemplateView):
    template_name = "tv.html"
    """
        Класс который отвечает за отображение телепрограммы,

        В коде часто встречается -timedelta(hours=5): Это служит для того, что диснеевская программа в отличии
        от обычного datetime начинается в 5 утра и заканчивается в 5 утра следующего дня.

    """

    def __init__(self, **kwargs):
        super(TvPage, self).__init__(**kwargs)
        self.filtred_title = ""

    def get_context_data(self, **kwargs):
        context = super(TvPage, self).get_context_data(**kwargs)
        context['active_days'],context['tv'] = self.get_tv_date()
        programm_id = self.request.GET.get('item', None)
        try:
            tv_program_item = TVProgramItem.objects.get(pk=programm_id)
            context['title'] = tv_program_item.program.title
        except TVProgramItem.DoesNotExist:
            context['title'] = ''

        return context

    @staticmethod
    def date_for_disney_programs():
        return datetime.today()

    @staticmethod
    def get_class_for_tv_item(date, local_time, current_tv_program):
        cls = ""
        if not local_time:
            local_time = TvPage.date_for_disney_programs()

        if date < local_time:
            cls = "past"

        if current_tv_program and date == current_tv_program.date_start:
            cls = "rightnow"

        return cls

    def day_description(self, day):
        data = dict()
        data['class'] = ''

        _date = TvPage.date_for_disney_programs() - timedelta(hours=5)

        if day == _date.date():
            data['title'] = u"Cегодня"
        elif day == _date.date() - timedelta(days=1):
            data['title'] = u"Вчера"
        elif day == _date.date() - timedelta(days=2):
            data['title'] = u"Позавчера"

        else:
            data['title'] = pytils.dt.ru_strftime(date=day, format="%a, %d")
        return data

    def get_tv_date(self):
        result = []
        week = CurrentTVWeekDates()

        #   do fetch stuff there
        days_to_gather = week.days_to_gather_programs()
        tv_programs = TVProgram.objects.filter(day__gte=days_to_gather[0]).filter(day__lte=days_to_gather[-1])
        days2program = {tv.day: self.generate_programm_day(tv) for tv in tv_programs}

        tz = self.request.session['user_time_zone']
        local_time = get_local_time(tz)
        current_tv_program = TVProgramItem.objects.current_tv_programm(tz=tz)

        #   composing and decorating results
        for prev, day, next in week.iter_neighborhood():
            day_tv = days2program.get(day, [])
            next_tv = days2program.get(next, [])
            disney_day_programs = self.mix_neighbor_days(day_tv, next_tv)
            disney_day_programs = self.decorate_programs(disney_day_programs, local_time, current_tv_program)
            result.append({
                'day_value': day,
                'day': self.day_description(day),
                'programs': disney_day_programs
            })

        current_date = TvPage.date_for_disney_programs() - timedelta(hours=5)
        current_date_value = current_date.date()

        result_has_program = []
        for item in result:
            if item['programs'] is None or len(item['programs']) == 0:
                item['day']['class'] = 'disable'
            else:
                result_has_program.append(item)

        def sortProgram(item1, item2):
            day1_value = item1['day_value']
            day2_value = item2['day_value']
            if day1_value == current_date_value: return 1
            if day1_value > current_date_value:
                if day1_value > day2_value: return -1
                if day1_value < day2_value: return 1
            if day1_value < current_date_value:
                if day1_value < day2_value: return -1
                if day1_value > day2_value: return 1

            return 0

        if len(result_has_program) > 0:
            result_sorted = sorted(result_has_program, cmp=sortProgram, reverse=True)
            result_sorted[0]['day']['class'] = 'active'

        return len(result_has_program),result

    def decorate_programs(self, programs, local_time, current_tv_program):
        result = []
        for i, item in enumerate(programs):
            ICS_DATETIME_FORMAT = '%Y%m%dT%H%M00'
            utc_delta = timedelta(hours=3)
            date_start = item.date_start
            date_end = item.date_end
            if not date_end:
                try:
                    next = programs[i+1]
                    date_end = next.date_start
                except IndexError:
                    date_end = item.date_start + timedelta(hours=1)

            item.date_start = self.adapt_datetime(item.date_start)
            cls = TvPage.get_class_for_tv_item(item.date_start, local_time, current_tv_program)
            can_schedule = item.program.can_schedule and cls == ""

            result.append({
                'item': item,
                'class': cls,
                'can_schedule': can_schedule,
                'date_start': date_start.strftime(ICS_DATETIME_FORMAT),
                'date_end': date_end.strftime(ICS_DATETIME_FORMAT),
                'date_start_utc': (date_start - utc_delta).strftime(ICS_DATETIME_FORMAT) + 'Z',
                'date_end_utc': (date_end - utc_delta).strftime(ICS_DATETIME_FORMAT) + 'Z',
            })
        return result

    def mix_neighbor_days(self, day_tv, next_tv):
        current_day = next_day = []

        if day_tv:
            current_day = filter(lambda x: x.date_start.hour >= 5, day_tv)
        if next_tv:
            next_day = filter(lambda x: x.date_start.hour < 5, next_tv)

        return current_day + next_day

    def generate_programm_day(self, obj):
        programs = obj.programs.filter(
#                    program__pk=query,
                program__not_show=False
        )

        programs = programs.order_by('date_start')
        programs = programs.prefetch_related('program')
        programs = list(programs.all())

        # Ugly huck to initialize `end_date`
        prev = None
        for p in programs:
            if prev and not prev.date_end:
                prev.date_end = p.date_start
            prev = p

        try:
            query = self.request.GET.get('item')
            if query:
                query = int(query)
                programs = filter(lambda p: p.program.pk == query, programs)
        except ValueError:
            pass

        return programs

    def adapt_datetime(self, dt):
        tz = self.request.session['user_time_zone']
        local_time = get_local_time(tz)
        match, hours = time_kanal_match(local_time)
        if match:
            return dt + timedelta(hours=hours)
        return dt


@csrf_exempt
@ajax_request
@user_passes_test(lambda user: user.is_superuser)  # Only superusers could use this function
def tv_file_parse(request):
    csv_file = request.FILES.get('file', None)
    parser = TVCSVParser(
            csv_file=csv_file
    )
    if parser.has_conflicts():
        return {
            'message': u"В процессе парсинга были найдены конфликты",
            'conflicts': parser.parsed_data()
        }

    return {'message': u"Данные успешно сохранены"}


@csrf_exempt
@ajax_request
@user_passes_test(lambda user: user.is_superuser)  # Only superusers could use this function
def tv_file_parse_conflicts(request):
    data = json.loads(request.body)
    if data['choice'] == 'final':

        if 'create' in data:
            for item in data['create']:
                program_date = datetime.strptime(item['date'] + item['time'], "%d.%m.%Y%H:%M")
                program_day = datetime.strptime(item['date'], "%d.%m.%Y")
                program, created = ProgramItem.objects.get_or_create(
                        title=item['title']
                )
                if created:
                    program.rating = item['rating']
                    program.save()

                tv_programm, created = TVProgram.objects.get_or_create(
                        day=program_day
                )
                tv_programm_item, created = TVProgramItem.objects.get_or_create(
                        program=program,
                        date_start=program_date
                )
                tv_programm.programs.add(tv_programm_item)

        if 'time' in data:
            for item in data['time']:
                program_date = datetime.strptime(
                        item['date'] + item['time'],
                        "%d.%m.%Y%H:%M"
                )
                program_day = datetime.strptime(
                        item['date'],
                        "%d.%m.%Y"
                )
                tv_programm, created = TVProgram.objects.get_or_create(
                        day=program_day
                )
                program, created = ProgramItem.objects.get_or_create(
                        title=item['title'],
                        rating=item['rating']
                )
                try:
                    program_to_out = tv_programm.programs.filter(
                            date_start=program_date
                    )
                    tv_programm.programs.remove(*program_to_out)
                except TVProgramItem.DoesNotExist:
                    pass
                tv_programm_item, created = TVProgramItem.objects.get_or_create(
                        program=program,
                        date_start=program_date
                )
                tv_programm.programs.add(tv_programm_item)

    return {'message': u"Конфликты успешно разрешены"}



ICS_TMP = u'''
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//hacksw/handcal//NONSGML v1.0//EN
BEGIN:VEVENT
DTSTAMP:{}
TZID:{}
ORGANIZER;CN=Канал Disney:MAILTO:region@kanal.disney.ru
DTSTART:{}
DTEND:{}
SUMMARY:{}
END:VEVENT
END:VCALENDAR
'''


## TODO: http://stackoverflow.com/questions/5329529/i-want-html-link-to-ics-file-to-open-in-calendar-app-when-clicked-currently-op

def get_tv_program_ics(request, *args, **kwargs):
    date_start = request.GET.get('date_start')
    date_end = request.GET.get('date_end')
    title = request.GET.get('title')
    tz = request.session['user_time_zone'].strip()
    program_id = kwargs.get('program_id')

    ics = ICS_TMP.format(date_start, tz, date_start, date_end, title, )
    #ics = ICS_TMP % (date_start, date_start, date_end, title, )
    response = HttpResponse(ics, content_type='text/calendar')
    response['Content-Disposition'] = 'attachment; filename=cal.ics'

    return response







"""
class MyView(TvPage,View):
     def serialize(self):
       """Return object data in easily serializeable format"""
       return { 'item' : self.id,
                'created': self.created.isoformat(),
                'dishes' : [ item.serialize() for item in self.dishes]}

    def get_tv_date(self):
        result = []
        week = CurrentTVWeekDates()

        #   do fetch stuff there
        days_to_gather = week.days_to_gather_programs()
        tv_programs = TVProgram.objects.filter(day__gte=days_to_gather[0]).filter(day__lte=days_to_gather[-1])
        days2program = {tv.day: self.generate_programm_day(tv) for tv in tv_programs}
        tz = self.request.session['user_time_zone']
        local_time = get_local_time(tz)
        current_tv_program = TVProgramItem.objects.current_tv_programm(tz=tz)
        for prev, day, next in week.iter_neighborhood():
            day_tv = days2program.get(day, [])
            next_tv = days2program.get(next, [])
            disney_day_programs = self.mix_neighbor_days(day_tv, next_tv)
            disney_day_programs = self.decorate_programs(disney_day_programs, local_time, current_tv_program)
            result.append({
                'day_value': day,
                'day': self.day_description(day),
                'programs': disney_day_programs
            })

        current_date = TvPage.date_for_disney_programs() - timedelta(hours=5)
        current_date_value = current_date.date()
        return result

    def get(self, *args, **kwargs):
        context = {}
        context= self.get_tv_date()
        serialized_obj = serializers.serialize('json', [ context, ])
        return JsonResponse(serialized_obj),safe=False)

"""

class MyView(ListModelMixin,GenericAPIView):
    week = CurrentTVWeekDates()
    days_to_gather = week.days_to_gather_programs()
    queryset = TVProgram.objects.filter(day__gte=days_to_gather[0]).filter(day__lte=days_to_gather[-1])
    serializer_class  = TVSERIALIZER
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


 def create_days(self):
        week = CurrentTVWeekDates()
        days_to_gather = week.days_to_gather_programs()
        dates = []
        for i in days_to_gather:
            dates.append(i.isoformat())
        return days_to_gather,dates
   
    def title_and_description(self,id):
        description = ProgramItem.objects.filter(id = id ).values("description")
        title = ProgramItem.objects.filter(id = id ).values("title")
        image = ProgramItem.objects.filter(id =id).values("cdn_image")
        cdn_image = item[0]['cdn_image'].url()
        return title,description,cdn_image

 
    def program_by_day(self,days_with_ids):
        date_with_programs = OrderedDict()
        for date,id in days_with_ids.items():
            date_with_programs[date] = TVProgramItem.objects.filter(programs=id).order_by('date_end')
        return date_with_programs

    def date_plus_id(self,days,ids):
        week = OrderedDict(zip(days,ids))
        return week
    
    def values_by_id(self,week,program):
        values = OrderedDict()
        for date,id in week.items():
            values[date] = program_by_day(id)
        return values


    def get(self,request):
        days_to_gather,days = self.create_days()
        tv_programs = TVProgram.objects.filter(day__gte=days_to_gather[0]).filter(day__lte=days_to_gather[-1])

        ids = [tv[0] for tv in tv_programs.values_list() ]
        days_with_ids = self.date_plus_id(days,ids)
        current_programs = self.program_by_day(days_with_ids) 
        #week = date_plus_id(days,ids) 
        #upload_programs = values_by_id(week,) 
        return JsonResponse((current_programs),safe =False)





    def get(self,request):
        results = []
        #cделали сетку дней
        days_to_gather,days = self.create_days()
        results.append()
        #по сетке вытаскиваем id программ
        tv_programs = TVProgram.objects.filter(day__gte=days_to_gather[0]).filter(day__lte=days_to_gather[-1])
        ids = [tv[0] for tv in tv_programs.values_list() ]
        #получили все дни с программами
        current_progrmas = map(self.program_by_day,ids)

        return Response(current_progrmas)
