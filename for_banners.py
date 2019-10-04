# coding=utf-8
import pytils, os, zipfile
from colorfield.fields import ColorField
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.core.urlresolvers import reverse
from apps.main.models import *
from django.db import models
from .validators import validate_zip_extension
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from apps.cdn.models import CDNField, post_cdn_save

#  These files need to be placed in separate project
#  with migrations (probably). ...later

class VideoItems(BaseOrderModel, SliderItem):
    class Meta:
        verbose_name_plural = u"Видео"
        verbose_name = u"видео"

    twigle_id = models.CharField(
        verbose_name="Twigle ID",
        max_length=255,
        blank=True,
        null=True
    )
    slug = models.SlugField(
        verbose_name=u'slug',
        editable=True,
        # unique=True,
        max_length=255,
        blank=True,
        null=True
    )
    meta_preview_url = models.URLField(
        verbose_name=u"Превью файла CDN",
        help_text=u"""
                  Превью видео будет автоматически обновлено при сохранении.
                  """,
        blank=True,
        null=True
    )
    meta_duration = models.CharField(
        verbose_name=u"Длительность видео",
        help_text=u"""
                  Длительность видео будет автоматически обновлено при сохранении.
                  """,
        max_length=255,
        blank=True,
        null=True
    )

    @property
    def twigle_url(self):
        return reverse('video_page', args=[self.twigle_id])

    @property
    def preview(self):
        if self.cdn_thumb:
            return self.cdn_thumb
        elif self.twigle_id and self.meta_preview_url:
            return self.meta_preview_url
        else:
            return None

    def save(self, *args, **kwargs):
        try:
            self.slug = pytils.translit.slugify(self.title)
        except:
            pass

        super(VideoItems, self).save(*args, **kwargs)


class GameItems(BaseOrderModel, SliderItem):
    class Meta:
        verbose_name_plural = u"Игры"
        verbose_name = u"игра"

    franchise = models.CharField(
        verbose_name=u"Франшиза",
        max_length=255,
        null=True,
        blank=True
    )


class BlockAppearance(models.Model):
    class Meta:
        verbose_name_plural = u"Оформления"
        verbose_name = u"оформление"

    bg_image = models.ImageField(
        verbose_name=u"Изображение фона",
        upload_to=u"slider",
        help_text=u"размер 2560x835",
        blank=True,
        null=True
    )
    cdn_bg_image = CDNField(
        parent_field=bg_image
    )
    bg_color = ColorField(verbose_name=u"Цвет фона", blank=True, null=True, default='#ffffff')
    top_gradient_color = ColorField(verbose_name=u"Цвет градиента сверху", blank=True, null=True, default='#ffffff')
    bottom_gradient_color = ColorField(verbose_name=u"Цвет градиента снизу", blank=True, null=True, default='#ffffff')

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    customizable_object = GenericForeignKey('content_type', 'object_id')

post_cdn_save(BlockAppearance)


class HeroUniversalItems(SliderItem, BaseOrderModel, GoogleAnalyticsItems):
    class Meta:
        verbose_name_plural = u"Объекты Hero Universal"
        verbose_name = u"объект Hero Universal"

    LEFT = 'left'
    RIGHT = 'right'
    CENTER = 'center'
    BUTTON_POSITIONS = (
        (LEFT, u"Слева"),
        (RIGHT, u"Справа"),
        (CENTER, u"В центре"),
    )
    button_positions = models.CharField(
        verbose_name=u"Позиция кнопки в слайде",
        choices=BUTTON_POSITIONS,
        default=LEFT,
        null=False,
        blank=False,
        max_length=255
    )
    button_text = models.CharField(
        verbose_name=u"Текст на кнопке",
        help_text=u"Если текст не указан, то кнопка не будет отображена",
        null=True,
        blank=True,
        max_length=255
    )
    mobile_thumb = models.ImageField(
        verbose_name=u"Изображение для мобильной версии",
        help_text=u"""
        размер 1534x670
        (будет отображена вместо фонового и
        переднего изображений одновременно)
        """,
        upload_to=u"slider_item",
        null=True,
        blank=True
    )
    cdn_mobile_thumb = CDNField(
        parent_field=mobile_thumb
    )
    tablet_thumb = models.ImageField(
        verbose_name=u"Изображение для планшетной версии",
        help_text=u"""
        размер 1536x568
        (будет отображена вместо фонового и
        переднего изображений одновременно)
        """,
        upload_to=u"slider_item",
        null=True,
        blank=True
    )
    cdn_tablet_thumb = CDNField(
        parent_field=tablet_thumb
    )
    html5_zip = models.FileField(
        verbose_name=u"Zip-архив для HTML5-баннера",
        help_text=u"zip-архив должен содержать к корне файл index.html",
        upload_to=u"html5/%Y/%m/%d/",
        validators=[validate_zip_extension],
        null=True,
        blank=True
    )
    target_blank = models.BooleanField(verbose_name=u'Открыть в новом окне',default=False)
    appearance_objects = GenericRelation(BlockAppearance)

    @property
    def html5_banner(self):
        if self.html5_zip is None or not self.html5_zip: return None
        dirname = 'media/' + os.path.splitext(self.html5_zip.name)[0]
        if os.path.exists(dirname + '/index.html'): return '/' + dirname + '/index.html'
        return None

    @property
    def appearance(self):
        return self.appearance_objects.first()

post_cdn_save(HeroUniversalItems)

class GallerySlider(models.Model):
    class Meta:
        verbose_name_plural = u"Галлереи"
        verbose_name = u"галлерея"

    title = models.CharField(
        verbose_name=u"Название",
        max_length=255
    )
    search_title = models.CharField(
        verbose_name=u"Заголовок",
        default=u"Галерея",
        help_text=u"(используется только для поиска в админке)",
        null=True,
        blank=True,
        max_length=255
    )
    description = models.CharField(
        verbose_name=u"Описания",
        max_length=255,
        blank=True,
        null=True
    )
    appearance_objects = GenericRelation(BlockAppearance)

    @property
    def sorted_items(self):
        return self.items.order_by('order', 'pk').all()

    @property
    def appearance(self):
        return self.appearance_objects.first()

    def __unicode__(self):
        return "%s - %s" % (self.search_title, self.title)

class GalleryItems(BaseOrderModel, SliderItem):
    class Meta:
        verbose_name_plural = u"Изображения галлереи"
        verbose_name = u"изображение"

    object = models.ForeignKey(GallerySlider,
                               blank=True,
                               null=True,
                               related_name="items")
post_cdn_save(GalleryItems)

@receiver(post_save, sender=HeroUniversalItems)
def extract_zip_archive(sender, instance, **kwargs):
    if not instance.html5_zip: return
    dirname = 'media/' + os.path.splitext(instance.html5_zip.name)[0]
    if os.path.exists(dirname): return
    os.makedirs(dirname)
    zip_ref = zipfile.ZipFile('media/' + instance.html5_zip.name, 'r')
    zip_ref.extractall(dirname)
    zip_ref.close()
