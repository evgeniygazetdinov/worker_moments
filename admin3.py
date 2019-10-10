# coding=utf-8
from django.contrib import admin
from apps.slider.models import SiteMainPageSlider
from django import forms
from django.contrib import messages
import pytils, os, zipfile


class SliderAdmin(admin.ModelAdmin):
    
    def save_model(self,request,obj,form,change):
        if obj.slider_type == 0:
            if obj.image == "":
                messages.set_level(request, messages.ERROR)
                messages.error(request,'нет картинки для компьютера')
            if obj.image_tablet == None:
                messages.set_level(request, messages.ERROR)
                messages.error(request,'нет картинки для планшета')
            if obj.image_mobile == None:
                messages.set_level(request, messages.ERROR)
                messages.error(request,'нет картинки для смартфона')
            #if obj.image_mobile == None or obj.image_tablet == None or obj.image_mobile == None and obj.slider_type ==1:
            #     
            else:
                obj.save()
            
        if obj.slider_type == 1:
            print(obj.html5_zip)
            if  obj.html5_zip == None:
                messages.set_level(request, messages.ERROR)
                messages.error(request,'нет архива')
            else:
                obj.save()
    
        
            


    list_display = ('ordering', 'title')
admin.site.register(SiteMainPageSlider, SliderAdmin)





        
