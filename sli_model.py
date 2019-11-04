# coding=utf-8
from django.db import models
from .validators import validate_zip_extension
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.dispatch import receiver
from django.db.models.signals import pre_save,post_save
import pytils, os, zipfile
import re

class SiteMainPageSlider(models.Model):

    class Meta:
        verbose_name_plural = u"Слайдер на главной странице"
        verbose_name = u"слайд"

    IMAGE_SLIDE = 0
    HTML_CODE_SLIDE = 1

    SLIDER_TYPES = (
        (IMAGE_SLIDE, u'Картинка'),
        (HTML_CODE_SLIDE, u'Встроенный баннер'),
    )

    ordering = models.IntegerField(u"Ранг сортировки", null=True, blank=True, default=0)

    slider_type = models.IntegerField(u"Тип слайда", choices=SLIDER_TYPES, default=IMAGE_SLIDE)
    title = models.CharField(u"Описание слайда", max_length=255, blank=True, null=True)

    image = models.ImageField(u"Картинка для компьютера", upload_to="slider",blank=True, help_text="Размер: 1024х409")
    image_tablet = models.ImageField(u"Картинка для планшета", upload_to="slider",null=True, blank=True, help_text="Размер: 700х409")
    image_mobile = models.ImageField(u"Картинка для смартфона", upload_to="slider", null=True, blank=True, help_text="Размер: 409х409")
    adfox_link = models.CharField(u"Ссылка для Adfox-пикселя", max_length=255, blank=True, null=True)
    link = models.CharField(u"Ссылка", max_length=255, help_text=u"Пример: /films/episodeI/. Если выбран тип 'Картинка'", blank=True, null=True)
    no_follow = models.BooleanField(u"Nofollow для ссылки", help_text=u"Включить rel=\"nofollow\" для ссылки", default=False)
    hide_knowmore = models.BooleanField(u"Скрыть \"Узнать больше\"", default=False)
    code = models.TextField(u"Код слайда", help_text=u"Если выбран тип 'Встроенный баннер'", blank=True, null=True)
    html5_zip = models.FileField(
        verbose_name=u"Zip-архив для HTML5-баннера",
        help_text=u"zip-архив должен содержать к корне файл index.html",
        upload_to = u"html5/",
        null=True,blank=True)#,validators=[validate_zip_extension])

    @property
    def html5_banner(self):
        if self.html5_zip is None or not self.html5_zip: return None
        dirname = 'media/' + os.path.splitext(self.html5_zip.name)[0]
        if os.path.exists(dirname + '/index.html'): return '/' + dirname + '/index.html'
        return None
 
    @property
    def property_path(self):
        property = {}
        return property    


    @property
    def appearance(self):
        return self.appearance_objects.first()

    def find_all_files(self,where):
        pictures = os.getcwd() + '/media/' + (os.path.splitext(self.html5_zip.name)[0])
        path = pictures + where
        files = {}
        tablet = r'tablet_\d+x\d+.'
        mobile = r'mobile_\d+x\d+.'
        desktop = r'desktop_\d+x\d+'
        print(path)
        for entry in os.listdir(path):
            if os.path.isfile(os.path.join(path, entry)):
                if re.match(tablet,entry,re.UNICODE):
                    print("has tablet")
                    files['tablet'] = os.path.join(path, entry)
                if re.match(mobile,entry,re.UNICODE) :
                    print("has phone")
                    files['mobile'] = os.path.join(path, entry)
                if re.match(desktop,entry,re.UNICODE): 
                    print("has desktop")
                    files['desktop']= os.path.join(path,entry)
                if entry.endswith('.mp4'):
                    print("has iframe")
                    files['iframe']= os.path.join(path,entry)
        return files
                

    def extract_zip_archive(self):
        if not self.html5_zip: return
        dirname = 'media/' + os.path.splitext(self.html5_zip.name)[0]
        if os.path.exists(dirname): return
        os.makedirs(dirname)
        zip_ref = zipfile.ZipFile('media/' + self.html5_zip.name, 'r')
        zip_ref.extractall(dirname)
        print(dirname)
        zip_ref.close()

    def __unicode__(self):
        return self.title

    def save(self,*args,**kwargs):
        super(SiteMainPageSlider,self).save(*args,**kwargs)
        self.extract_zip_archive()
        pict = self.find_all_files('/images/')
        iframe = self.find_all_files('/media/')
        self.code = str(iframe['iframe'])
        self.image = pict['desktop']
        self.image_tablet = pict['tablet']
        self.image_mobile = pict['mobile']
        super(SiteMainPageSlider,self).save(*args,**kwargs)
