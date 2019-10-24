# coding=utf-8
import pytils
from apps.tv.models import TVProgramItem,TVProgram
from rest_framework import serializers
from apps.programms.models import ProgramItem

class TVSERIALIZER(serializers.ModelSerializer):
    title = serializers.ReadOnlyField(source='program.title')
    class Meta:
        model = TVProgramItem
        fields = ('program')


class TVSheduleSerializer(serializers.ModelSerializer):
    days = serializers.SerializerMethodField(method_name ="")






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


class AdminTVProgrammSerializer(TVProgrammsSerializer):
    def start_date(self, obj):
        return obj.date_start.strftime('%d.%m.%Y')

class SuperSerializer(serializers.ModelSerializer):
    watch_now = serializers.SerializerMethodField('programs_on_day')

    def programs_on_day(self,obj):
        qs = TVProgramItem.objects.filter(programs = obj.pk).order_by('date_end')
        serializer = TVProgrammsSerializer(instance=qs, many=True)
        return serializer.data
    
    
    class Meta:
        model = TVProgram
        fields = ('day','watch_now')