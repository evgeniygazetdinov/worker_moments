from django.contrib import admin
from apps.slider.models import SiteMainPageSlider
from django import forms
from django.contrib import messages
import pytils, os, zipfile


class SliderAdmin(admin.ModelAdmin):

    def extract_before(self,obj):
        dirname = os.path.abspath(obj.html5_zip.name)
        if os.path.exists(dirname):
            os.makedirs(obj.html5_zip.name)
            print('we here')
            zip_ref = zipfile.ZipFile('media/html5/' + obj.html5_zip.name, 'r')
            zip_ref.extractall(dirname)
            zip_ref.close()


    def find_picture_for_banner(self,obj):
        mobile = r'mobile'
        tablet = r'tablet'
        pc = r'\d{3,}'
        self.extract_before(obj)
        print('extracted')

        print(("html5/"+str(obj.html5_zip).split('.zip')[0]+"/images/"))
        """
        for root, dirs, files in os.walk(str(path)):
            print('we here')
            for file in files:
                if file.endswith(".jpg") or file.endswith(".jpeg") or file.endswith(".png"):
                    if re.match(mobile,file):
                        mobile = file
                    if re.match(tablet,file):
                        obj.image_mobile = file 
                    elif re.match(pc,file):
                       obj.image_tablet = file
        """


    def save_model(self,request,obj,form,change):
        ordering =+1
        if obj.slider_type == 0:
            pass 
            #messages.error(request,'unbound type')
            obj.save()


        if obj.slider_type == 1:
            if obj.html5_zip is not None:
                print('True')
                obj.image_mobile, obj.image_tablet, obj.image = self.find_picture_for_banner(obj) 
                obj.save()
        
            


    list_display = ('ordering', 'title')
admin.site.register(SiteMainPageSlider, SliderAdmin)




"""
@receiver(post_save,sender = SiteMainPageSlider)
def validate_slider(sender,instance,**kwargs):
    mobile = r'mobile'
    tablet = r'tablet'
    pc = r'\d{3,}'
    print(dir(instance))
    if instance.slider_type == 1:
        print("executed")
        for r,d,f in os.walk('media/' + os.path.splitext(instance.html5_zip.name)[0]+'/images'):
            for file in f:
                if re.match(mobile,file):
                    instance.image_mobile = file
                if re.match(mobile,file):
                    instance.image_mobile = file 
                elif re.match(tablet,file):
                    instance.image_tablet = file
    else:
        print('THIS ELSE')
        class SiteMainPageSlider(models.Model): 
            image_mobile = models.ImageField(blank = False)
            image = models.ImageField(blank = False)
            image_tablet = models.ImageField(blank = False)
"""
        
