# coding=utf-8

from django import template
from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from apps.flatpages.models import Flatpage
from apps.main.models import Seodata
from apps.main.templatetags import string
from apps.programms.models import AdditionalTypes, ProgramItem
from cgi import escape
from apps.tv.utils import CurrentTVWeekDates
from apps.tv.models import TVProgram, TVProgramItem

register = template.Library()

@register.simple_tag(takes_context=True)
def shedule_ids(context):
    ids =[]
    slug = context['request'].resolver_match.kwargs.get('slug')
    try:
        ids = find_week_days(slug)
    except:
        return ''
    return '<meta property="{}" id="{}" />'.format('shedule_ids',ids)


@register.simple_tag(takes_context=True)
def seotag(context, type):
    seo, _ = get_seo_by_context(context)
    content = ''
    if seo: content = getattr(seo, 'seo_' + type)
    if not content: return ''
    return '<meta name="%(type)s" content="%(content)s" />' % {
        "type": type,
        "content": content,
    }

@register.simple_tag(takes_context=True)
def ogtag(context, type):
    seo, finded = get_seo_by_context(context)
    content = ''
    if seo: content = getattr(seo, 'og_' + type)
    if not content and ('image' != type or not finded ) and ('schedule_ids' != type): return ''
    if not content:
        try:
            content = string.get_domain(context) + finded.image.url
        except:
            return ''
    elif 'image' == type: 
        content = string.get_domain(context) + content.url
    return '<meta property="og:%(type)s" content="%(content)s" />' % {
        "type": type,
        "content": escape(content),
    }







@register.simple_tag(takes_context=True)
def social_sharing(context):
    seo, _ = get_seo_by_context(context)
    content = ''
    if not seo or not seo.social_sharing: return ''
    return '''
    <div class="dmodule__sharing">
      <span>Поделиться</span>
      <div class="dmodule__sharing_links">
        <a href="https://www.facebook.com/sharer" target="_blank" class="dmodule__sharing_facebook">Facebook</a>
        <a href="https://twitter.com/share" target="_blank" class="dmodule__sharing_twitter">Twitter</a>
        <a href="https://connect.ok.ru/offer" target="_blank" class="dmodule__sharing_ok">Одноклассники</a>
      </div>
    </div>
    <div class="dmodule__sharing_clear"></div>
    '''




def get_seo_by_context(context):
    slug, url_name = context['request'].resolver_match.kwargs.get('slug'), context['request'].resolver_match.url_name
    content = ''
    seo = None
    find_by_slug = None
    if None != slug:
        try:
            replace_names = {
                'additional-programm-detail': ['specialsserials', 'cartoonserials', 'serials', 'cartoons'],
                'serial': 'animationserial',
                'news_item': 'news',
                'film': 'films',
                'banimation': 'biganimation',
                'programm': 'programs',
                'character': 'characters'
            }
            if url_name in replace_names:
                url_name = replace_names[url_name]

            if not isinstance(url_name, list): url_name = [url_name]
            for un in url_name:
                try:
                    mod = ContentType.objects.get(model=un)
                    res_model = apps.get_model(mod.app_label, un)
                    find_by_slug = res_model.objects.get(slug=slug)
                    seo = Seodata.objects.get(content_type=ContentType.objects.get_for_model(res_model), object_id=find_by_slug.id)
                    if seo: break
                except:
                    continue
            raise
        except:
            try:
                find_by_slug = Flatpage.objects.get(url=context['request'].path)
                seo = Seodata.objects.get(content_type=ContentType.objects.get_for_model(Flatpage), object_id=find_by_slug.id)
            except:
                pass
    else:
        try:
            seo = Seodata.objects.get(seo_url=context['request'].path)
        except:
            pass
    if seo is None:
        try:
            find_by_slug = ProgramItem.objects.get(slug=slug)
            for addType in AdditionalTypes.objects.all():
                try:
                    seo = Seodata.objects.get(content_type=ContentType.objects.get_for_model(ProgramItem), object_id=find_by_slug.id)
                    if seo: break
                except:
                    continue
        except: pass
    return seo, find_by_slug





def find_week_days(slug):
    #programs with exist shudule
    week = CurrentTVWeekDates()
    days_to_gather = week.days_to_gather_programs()
    #find  schedule days
    queryset = TVProgram.objects.filter(day__gte=days_to_gather[0]).filter(day__lte=days_to_gather[-1])
    #find_program id by slug
    program_id = ProgramItem.objects.get(slug=slug)
    on_week_id = []
    for i in range(len(queryset)):
        on_day = queryset[i].programs.filter(program_id = program_id).values_list('id',flat = True)
        if len(on_day) != 0:
            on_week_id.append(on_day[0])
    
    return on_week_id

