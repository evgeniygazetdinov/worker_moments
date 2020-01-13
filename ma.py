from django.views.generic import TemplateView
from django.shortcuts import render
from django.views.generic import View
from django.db.models import Count, Max


class IndexPage(TemplateView):
    template_name = "index.html"
    ITEMS_PER_PAGE = 10

    @property
    def current_tv_getter(self):
        timezone = self.request.session['user_time_zone']
        return TVProgramItem.objects.current_tv_programm(tz=timezone)


    def remove_duplicates(self):
        unique_fields = ['program', 'date_start']
        duplicates = (
        TVProgramItem.objects.values(*unique_fields).order_by().annotate(max_id=Max('id'), count_id=Count('id')).filter(count_id__gt=1))
        for duplicate in duplicates:
            (TVProgramItem.objects.filter(**{x: duplicate[x] for x in unique_fields}).exclude(id=duplicate['max_id']).delete())


    def get_context_data(self, *args, **kwargs):
        self.remove_duplicates()
        timezone = self.request.session['user_time_zone']
        current_tv = TVProgramItem.objects.current_tv_programm(tz=timezone)
        tv = TVProgramItem.objects.tv_programm(tz=timezone)[:self.ITEMS_PER_PAGE]
        context = super(IndexPage, self).get_context_data(**kwargs)
        context['faq'] = FAQ.objects.filter(show=True)[:3]
        context['programs'] = Programs.objects.all()
        context['animation'] = TVProgramItem.objects.big_animation(tz=timezone)[:self.ITEMS_PER_PAGE]
        context['projects'] = AnimationSerial.objects.filter(not_show=False)
        context['films'] = Films.objects.all()[:self.ITEMS_PER_PAGE]
        context['current_tv'] = current_tv
        context['tv'] = [current_tv] + list(tv)
        context['news'] = News.objects.main_page_news()

        if self.request.GET.get('shared-voting'):
            shared = Contest.objects.active().all().first()
            context['shared'] = shared

        return context



class Redirect404View(View):
    """
    View for 404 redirect
    """

    def get(self, request, *args):
        html = '404.html'
        context = {}
        return render(request, html, context, status=404)


class Redirect500View(View):
    """
    View for 500 redirect
    """
    def get(self, request, *args):
        html = '500.html'
        context = {}
        return render(request, html, context, status=500)
