from apps.slider.models import SiteMainPageSlider
from django import template

register = template.Library()



def handler_zip_file(path):
    zip = str(path).split('.zip')
    index_path = 'media/'+zip[0]+'/index.html'
    return index_path


@register.simple_tag
def render_slide(slide, index):
    if slide.slider_type == SiteMainPageSlider.IMAGE_SLIDE:
        return """
                  <li%(hide_knowmore)s><a class="item"
                         href="%(link)s"
                         data-more-href="%(link)s" %(no_follow)s
                         data-gav="v1"
                         data-gav__clickable
                         data-gav__label-view="%(gav_label)s"
                         data-gav__event-view="InternalPromoViewBranding"
                         data-gav__label-click="%(gav_label)s"
                         data-gav__event-click="InternalPromoClickBranding">

                      <img src="%(image)s"
                           src-tablet="%(image_tablet)s"
                           src-mobile="%(image_mobile)s"
                           src-screen="%(image)s"
                           alt="" class="img-responsive">
                  </a></li>
        """ % {
            'gav_label': u"{0} | Slot{1} | {2}".format(slide.title, index, slide.link),
            'link': slide.link,
            'image': slide.image.url,
            'image_tablet': slide.image_tablet.url,
            'image_mobile': slide.image_mobile.url,
            'no_follow': ('rel="nofollow"' if slide.no_follow else ''),
            'hide_knowmore': (' data-slider-hide_knowmore' if slide.hide_knowmore else '')}

    else:
        slider = handler_zip_file(slide.html5_zip.name)
        #   HTML_CODE_SLIDE
       
        return """
             <li{hide_knowmore}>
            <a href="{link}" data-more-href="{link}" class="main_slider__full_link" {no_follow}
                data-gav="v1"
                data-gav__clickable
                data-gav__label-view="{gav_label}"
                data-gav__event-view="InternalPromoViewBranding"
                data-gav__label-click="{gav_label}"
                data-gav__event-click="InternalPromoClickBranding"></a>
                <div class="iframe-wrapper" >
                    <iframe src="{slider}" class="img-responsive" style ="height:400px;width: 100%;" crolling="no"></iframe>
                </div>    
            </li>
        """.format(index = index, no_follow = ('rel="nofollow"' if slide.no_follow else ''), 
        link = slide.link, slider = slide.html5_banner, hide_knowmore=('data-slider-hide_knowmore' if slide.hide_knowmore else ''),
        gav_label = "{slide} | slot{index} | {link}".format(slide = slide.html5_banner, index = index,link = slide.html5_banner))
        


    #tut goret budem
    



