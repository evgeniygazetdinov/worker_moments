# coding=utf-8
import pytils
from apps.tv.models import TVProgramItem,TVProgram
from rest_framework import serializers
from apps.programms.models import ProgramItem


class TVProgrammsSerializer(serializers.ModelSerializer):
    time = serializers.SerializerMethodField(method_name='tv_time')
    date_start = serializers.SerializerMethodField(method_name='date_start')
    date_end = serializers.SerializerMethodField(method_name='')
    url = serializers.ReadOnlyField(source='get_absolute_url')
    title = serializers.ReadOnlyField(source='program.title')
    rating = serializers.ReadOnlyField(source='program.rating')
    image = serializers.SerializerMethodField('get_image_relative_url')

    def get_image_relative_url(self, obj):
        if obj and obj.program and obj.program.image:
            return obj.program.image.url
        return ''

    def tv_time(self, obj):
        return obj.date_start.strftime("%H:%M")

    def start_date(self, obj):
        return pytils.dt.ru_strftime(
            date=obj.date_start,
            format="%a, %d %b"
        )

    class Meta:
        model = TVProgramItem
        fields = (
            'id',
            'time',
            'date',
            'rating',
            'title',
            'image',
            'url',
        )

class TVProgramsSchedulerSerializer(TVProgrammsSerializer):
    image = serializers.SerializerMethodField(method_name='get_image_relative_url')
    url = serializers.SerializerMethodField(method_name='get_program_url')
    add_to_schedule = serializers.SerializerMethodField(method_name='button_schedule')

     def time_format(self,obj):
        return  obj.date_start.strftime("%Y%m%dT%H%M%S")

   def button_schedule(self,obj):
        if obj.program.can_schedule == True:
            #radical
            import sys 
            reload(sys)  
            sys.setdefaultencoding('utf8')
            #add to each word %20 for sticky in url 
            button_titles = "Посмотреть%20<<{title}>>на%20Канале%20Disney%20по%20телевизору!".format(title = "%20".join(str(obj.program.title.decode()).split()))
            return "{host}/tv/do-schedule/{id}?date_start={date_start}&{date_end}&tz={tz}&title={title}".format(host=self.context['request'],
                    id=obj.program.id,tz = self.context['timezone'], date_start = self.time_format(obj),
                    date_end = obj.date_end, title = button_titles)
        else:
            return ''


    def get_program_url(self,obj):
        if obj:
            pattern_protocol = '\w+://\w+.\w+'
            without_protocol = '/\w+\w+/'
            name = str(obj.get_absolute_url())
            if (re.match(without_protocol,name) is not None):
                if name is not None:
                    return str(self.context['request'])+str(obj.get_absolute_url())
            if (re.match(pattern_protocol,name) is not None):
                if name is not None:
                        return str(obj.get_absolute_url())
        else:
            return ''


    def get_image_relative_url(self, obj):
        if obj and obj.program and obj.program.image:
            pattern_protocol = '\w+://\w+.\w+'
            without_protocol = '/\w+\w+/'
            name = obj.program.image.url
            if (re.match(without_protocol,name) is not None):
                if name is not None:
                    return str(self.context['request'])+str(obj.program.image.url)
            if (re.match(pattern_protocol,name) is not None):
                if name is not None:
                        return obj.program.image.url
        else:
            return ''
    
    
    class Meta:
        model = TVProgramItem
        fields = ( 
            'id',
            'time',
            'date',
            'rating',
            'title',
            'image',
            'url',
            'add_to_schedule'
        )




class AdminTVProgrammSerializer(TVProgrammsSerializer):
    def start_date(self, obj):
        return obj.date_start.strftime('%d.%m.%Y')


class SuperSerializer(serializers.ModelSerializer):
    watch_now = serializers.SerializerMethodField('programs_on_day')

    def programs_on_day(self,obj):
        qs = TVProgramItem.objects.filter(programs = obj.pk).order_by('date_end')
        serializer = TVProgramsSchedulerSerializer(instance=qs, many=True)
        return serializer.data
    
    class Meta:
        model = TVProgram
        fields = ('day','watch_now')